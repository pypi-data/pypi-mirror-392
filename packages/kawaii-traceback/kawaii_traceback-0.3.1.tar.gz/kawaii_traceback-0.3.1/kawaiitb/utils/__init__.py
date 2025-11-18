import os
import site
import sys
from functools import lru_cache
from io import TextIOWrapper, StringIO
from pathlib import Path
from typing import Any, Callable, TextIO, Union, overload

import kawaiitb.utils.fromtraceback as fromtraceback

sys_getframe = sys._getframe  # noqa

readables = (TextIO, TextIOWrapper, StringIO)
SupportsReading = Union[*readables]

__all__ = ["sys_getframe", "extract_caret_anchors_from_line_segment", "safe_string",
           "fromtraceback", "is_sysstdlib_name", *fromtraceback.__all__, ]


def safe_string(value: Any, what: str, func: Callable[[Any], str] = str):
    try:
        return func(value)
    except:
        return f'<{what} {func.__name__}() failed>'


def is_sysstdlib_name(name: str) -> bool:
    return name in sys.builtin_module_names or name in sys.stdlib_module_names


def extract_caret_anchors_from_line_segment(segment):
    import ast

    try:
        tree = ast.parse(segment)
    except SyntaxError:
        return None

    if len(tree.body) != 1:
        return None

    normalize = lambda offset: fromtraceback.byte_offset_to_character_offset(segment, offset)
    statement = tree.body[0]
    match statement:
        case ast.Expr(expr):
            match expr:
                case ast.BinOp():
                    operator_start = normalize(expr.left.end_col_offset)
                    operator_end = normalize(expr.right.col_offset)
                    operator_str = segment[operator_start:operator_end]
                    operator_offset = len(operator_str) - len(operator_str.lstrip())

                    left_anchor = expr.left.end_col_offset + operator_offset
                    right_anchor = left_anchor + 1
                    if operator_offset + 1 < len(operator_str) and not operator_str[operator_offset + 1].isspace():
                        right_anchor += 1

                    while left_anchor < len(segment) and ((ch := segment[left_anchor]).isspace() or ch in ")#"):
                        left_anchor += 1
                        right_anchor += 1
                    return normalize(left_anchor), normalize(right_anchor)
                case ast.Subscript():
                    left_anchor = normalize(expr.value.end_col_offset)
                    right_anchor = normalize(expr.slice.end_col_offset + 1)
                    while left_anchor < len(segment) and ((ch := segment[left_anchor]).isspace() or ch != "["):
                        left_anchor += 1
                    while right_anchor < len(segment) and ((ch := segment[right_anchor]).isspace() or ch != "]"):
                        right_anchor += 1
                    if right_anchor < len(segment):
                        right_anchor += 1
                    return left_anchor, right_anchor

    return None

def _combine_subpath(file_exec_path, frame_co_filename) -> str:
    """
    安全地补全b_path的绝对路径，优先匹配最后面的相同目录

    Args:
        file_exec_path: 执行中的__file__的绝对路径
        frame_co_filename: 需要补全的相对路径

    Returns:
        补全后的绝对路径
    """
    # 将路径转换为Path对象并标准化
    a_abs = Path(file_exec_path).resolve()
    b_parts = Path(frame_co_filename).parts

    # 将a_path转换为目录列表
    a_parts = list(a_abs.parts)

    # 在a_path中从后往前查找与b_path开头匹配的位置
    b_start = b_parts[0]
    match_indices = []

    # 找到所有可能的匹配位置
    for i in range(len(a_parts) - 1, -1, -1):
        if a_parts[i] == b_start:
            match_indices.append(i)

    if not match_indices:
        raise ValueError(f"在路径 {file_exec_path} 中找不到与 {b_start} 匹配的目录")

    # 尝试每个匹配位置，找到最合适的
    for match_idx in match_indices:
        # 检查从这个位置开始是否能完整匹配b_path的开头部分
        match_len = min(len(a_parts) - match_idx, len(b_parts))
        can_match = True

        for j in range(match_len):
            if a_parts[match_idx + j] != b_parts[j]:
                can_match = False
                break

        if can_match:
            # 构建补全路径：a_path的前面部分 + b_path的剩余部分
            result_parts = a_parts[:match_idx] + list(b_parts)
            return str(Path(*result_parts))

    # 如果没有完整匹配，使用最后一个匹配位置
    last_match_idx = match_indices[0]  # 因为是从后往前找的，第一个就是最后一个匹配
    result_parts = a_parts[:last_match_idx] + list(b_parts)
    return str(Path(*result_parts))

def get_module_file_combined_key(frame, frame_co_filename=None) -> str:
    """获取模块的完整路径"""
    @lru_cache
    def unsafe_get_module_file_key(frame, frame_co_filename=None):
        file_exec_path = frame.f_globals.get('__file__', None)
        if not file_exec_path:
            return frame_co_filename
        if frame_co_filename and os.path.isabs(file_exec_path):
            return _combine_subpath(file_exec_path, frame_co_filename)
        return _combine_subpath(file_exec_path, frame_co_filename)
    try:
        filename = unsafe_get_module_file_key(frame, frame_co_filename)
    except:
        filename = frame.f_code.co_filename
    # print(f'[DEBUG] get_module_file_key: turn {frame.f_code.co_filename} -> {filename}')
    return filename

def get_module_exec_file(frame) -> str | None:
    """获取模块的执行文件路径"""
    return frame.f_globals.get('__file__', None)

def parse_filename_sp_namespace(filename: str, env = None) -> tuple[str, str]:
    """处理模块文件名，返回格式化后的命名空间和显示字符串"""

    if not env:
        return '', filename

    # 标准化路径，确保使用相同的分隔符
    filename = os.path.normpath(filename)
    cwd = os.path.normpath(env.cwd)

    def _parse_path_with_site_packages(filename: str, base_path: str) -> tuple[str, str] | None:
        """解析路径，处理标准库和site-packages中的模块"""
        if filename.startswith(base_path):
            rel_path = os.path.relpath(filename, base_path)
            parts = rel_path.split(os.sep)

            # 处理site-packages中的第三方库
            if len(parts) > 1 and parts[0] == 'site-packages':
                package_name = parts[1]
                if package_name.endswith('.py'):
                    package_name = package_name[:-3]
                return package_name, str(os.path.join(*parts[1:]))
            else:
                first_part = parts[0]  # 必须为第一目录，不能向后逐个查找
                if first_part and not first_part.startswith('__') and first_part.lower() not in env.get_invalid_site_packages_paths():
                    module_name = first_part
                    if module_name.endswith('.py'):
                        module_name = module_name[:-3]
                    return module_name, str(os.path.join(*parts))
                else:
                    return None
        return None

    # 检查是否在relative to工作目录下的虚拟环境下。提前检查避免误认为是工作目录。
    for path in env.site_packages_paths_which_after_cwd:
        result = _parse_path_with_site_packages(filename, str(path))
        if result:
            return result

    # 检查是否在工作目录下
    if filename.startswith(cwd):
        rel_path = os.path.relpath(filename, cwd)
        return '.', rel_path

    # 检查是否在库路径下（包括标准库和site-packages）
    for path in env.site_packages_paths - env.site_packages_paths_which_after_cwd:
        result = _parse_path_with_site_packages(filename, str(path))
        if result:
            return result

    # 默认情况，返回文件名
    base_name = os.path.basename(filename)
    if base_name.endswith('.py'):
        base_name = base_name[:-3]
    return base_name, base_name

def get_this_module_frame():
    # TODO: 删掉
    return sys_getframe(0)
