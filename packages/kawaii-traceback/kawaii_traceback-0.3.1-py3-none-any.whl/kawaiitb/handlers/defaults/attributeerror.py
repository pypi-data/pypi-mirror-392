from typing import Generator, TYPE_CHECKING
import inspect

import astroid
from astroid import nodes

from kawaiitb.kraceback import KTBException, ENV
from kawaiitb.kwihandler import ErrorSuggestHandler
from kawaiitb.runtimeconfig import rc
from kawaiitb.utils import safe_string, is_sysstdlib_name
from kawaiitb.utils.suggestions import find_weighted_closest_matches, VarsGroup, merge_sorted_suggestions
if TYPE_CHECKING:
    from kawaiitb.kraceback import FrameSummary


@KTBException.register
class AttributeErrorHandler(ErrorSuggestHandler, priority=1.0):
    def __init__(self, exc_type, exc_value: AttributeError, exc_traceback, **kwargs):
        super().__init__(exc_type, exc_value, exc_traceback, **kwargs)
        self._can_handle = issubclass(exc_type, AttributeError)
        if not self._can_handle:
            return
        self.msg = safe_string(exc_value, "<exception>")
        obj = exc_value.obj
        self.obj = obj
        self.wrong_name = exc_value.name
        self.obj_rawname = safe_string(obj, "<unknown obj>")
        self.obj_type = safe_string(type(obj).__name__, "<unknown type>")
        self.obj_is_none = obj is None
        self.obj_is_module = False if obj is None else inspect.ismodule(obj)
        self.obj_module_name = getattr(obj, "__name__") if self.obj_is_module else None
        self.candidates = None
        try:
            self.candidates = dir(obj)
        except:
            pass

    def can_handle(self, etype: KTBException) -> bool:
        return self._can_handle

    @classmethod
    def translation_keys(cls):
        return {
            "default": {
                "native.AttributeError.premsg": "The '{obj}' of type {type_} has no attribute '{name}'.",
                "native.AttributeError.modulepremsg": "Module {obj_module_name} has no attribute '{name}'.",
                "native.AttributeError.circular_import": "This might be caused by a circular import.",
                "native.AttributeError.single_suggest": "Did you mean {suggest}?",
                "native.AttributeError.multiple_suggest": "Did you mean one of {suggest}?",
                "native.AttributeError.many_suggest": "Did you mean one of {suggest}?",
                "native.AttributeError.no_suggest": "",
                "native.AttributeError.list_all_property": "This object has the following attributes: {all}",
                "native.AttributeError.list_all_callable": "This object has the following methods: {all}",
                "native.AttributeError.no_any_prop": "This object has no attributes or methods!",
                "native.AttributeError.rename_from_shadowing_stdlib": "Module '{obj}' shadows a standard library module. '{attr}' exists in the corresponding standard library.\n",
                "native.AttributeError.rename_from_shadowing_stdlib_var": "Variable '{obj}' shadows a standard library module. '{attr}' exists in the corresponding standard library.\n",
                "native.AttributeError.interdependents_with_loop": "This is likely caused by a circular import, as the module has not completed initialization. Possible import cycle:\n{path}",
                "native.AttributeError.interdependents_no_info": "This is likely caused by a circular import, as the module has not completed initialization.",
                "native.AttributeError.interdependents_loop_table_top": "+->+",
                "native.AttributeError.interdependents_loop_table_mid": "| |",
                "native.AttributeError.interdependents_loop_table_low": "+<-+",
            },
            "zh_hans": {
                "native.AttributeError.premsg": "{type_} 类型的 '{obj}' 没有属性 '{name}'。",
                "native.AttributeError.modulepremsg": "模块 {obj_module_name} 没有属性 '{name}'。",
                "native.AttributeError.circular_import": "可能是循环导入导致的。",
                "native.AttributeError.single_suggest": "你可能想试试 {suggest}?",
                "native.AttributeError.multiple_suggest": "你可能想试试 {suggest}?",
                "native.AttributeError.many_suggest": "你可能想试试 {suggest}?",
                "native.AttributeError.no_suggest": "",
                "native.AttributeError.list_all_property": "该对象拥有以下属性: {all}{extra}",
                "native.AttributeError.list_all_callable": "该对象拥有以下方法: {all}{extra}",
                "native.AttributeError.no_any_prop": "该对象没有任何属性或方法！",
                "native.AttributeError.rename_from_shadowing_stdlib": "模块 '{obj}' 的名字覆盖了标准库模块。'{attr}' 存在于对应的标准库中。\n",
                "native.AttributeError.rename_from_shadowing_stdlib_var": "变量 '{obj}' 的名字覆盖了标准库模块。'{attr}' 存在于对应的标准库中。\n",
                "native.AttributeError.interdependents_with_loop": "这个问题很可能是循环导入导致的，因为该模块还完成初始化。可能的导入环如下: \n{path}",
                "native.AttributeError.interdependents_no_info": "这个问题很可能是循环导入导致的，因为该模块还未完成初始化。",
                "native.AttributeError.interdependents_loop_table_top": "┌→┐",
                "native.AttributeError.interdependents_loop_table_mid": "│ │",
                "native.AttributeError.interdependents_loop_table_low": "└←┘",
                "native.AttributeError.max_suggest_list": 20,  # 不建议改
            }
        }

    def handle(self, ktb_exc: KTBException) -> Generator[str, None, None]:
        yield from self._handle(ktb_exc)

    def _default_handle(self):
        if not self.msg:
            yield rc.exc_line("AttributeError", rc.translate("native.AttributeError.default"))
        else:
            yield rc.exc_line("AttributeError", self.msg)

    def get_interdependent_nodes(self, ktb_exc: KTBException):
        """
        基于可能的循环导入检查tb，如果找到循环环，返回循环链。否则返回None
        """
        if not self.obj_is_module or not ktb_exc or len(ktb_exc.stack) == 0:
            return None  # 不是模块/没有tb, 无法判断
        if not hasattr(self.obj, '__file__'):
            return None
        error_ocuring_file = getattr(self.obj, '__file__')
        start_recording = False
        interdependent_nodes: list["FrameSummary"] = []
        for frame in ktb_exc.stack:
            if frame.abs_filename == error_ocuring_file:
                start_recording = True
            if start_recording:
                interdependent_nodes.append(frame)
        if len(interdependent_nodes) == 0:
            return None  # 不成环
        return interdependent_nodes  # 成环

    def _handle(self, ktb_exc: KTBException) -> Generator[str, None, None]:
        # 如果对象本身就有问题, 直接返回
        if not isinstance(self.wrong_name, str) or self.obj_is_none:
            yield from self._default_handle()
        if self.candidates is not None:
            candidates = self.candidates
        else:
            yield from self._default_handle()
            return

        # 获取代码当时使用时的情况
        if len(ktb_exc.stack) == 0:
            yield from self._default_handle()
            return

        # UC: 可调用对象(public, callable)
        # UP: 不可调用对象(public, property)
        # RC: 私有可调用对象(private, callable)
        # RP: 私有不可调用对象(private, property)
        # DU: 双下划线对象(double underscore)
        wrong_usage_type: VarsGroup
        # 是否私有
        wrong_usage_type = "R" if self.wrong_name.startswith('_') else "U"  # noqa
        # 是否可调用
        exc_frame = ktb_exc.stack[0]
        obj_rawname = self.obj_rawname
        attr_rawname = self.wrong_name
        for node in self.parse_ast_from_exc(exc_frame):
            if isinstance(node, (nodes.Import, nodes.ImportFrom)):
                extra_hint = ""
                if is_sysstdlib_name(self.obj_rawname) and self.obj_is_module:
                    extra_hint = rc.translate("native.AttributeError.rename_from_shadowing_stdlib")
                yield rc.exc_line("AttributeError", rc.translate("native.AttributeError.modulepremsg",
                                                                 obj_module_name=self.obj_module_name,
                                                                 name=attr_rawname) + extra_hint)
                break
            if isinstance(node, nodes.Attribute):
                if not isinstance(node.expr, (nodes.Name, nodes.Const)):  # 找出最终的不可进一步分解的节点
                    continue
                obj_rawname = node.expr.as_string()
                attr_rawname = node.attrname

                if is_sysstdlib_name(obj_rawname):
                    orig_lib = __import__(obj_rawname)
                    try:
                        getattr(orig_lib, attr_rawname)
                        if self.obj_is_module:
                            yield rc.translate('native.AttributeError.rename_from_shadowing_stdlib', obj=obj_rawname, attr=attr_rawname)
                        else:
                            yield rc.translate('native.AttributeError.rename_from_shadowing_stdlib_var', obj=obj_rawname, attr=attr_rawname)
                    except AttributeError:
                        pass


                if isinstance(node.parent, nodes.Call):
                    wrong_usage_type += "C"
                else:
                    wrong_usage_type += "P"
                break
        else:
            # never find an availd Attribute node
            yield from self._default_handle()
            return

        if "most likely due to a circular import" in str(ktb_exc):
            if loop := self.get_interdependent_nodes(ktb_exc):
                path = ""
                path_top = rc.translate("native.AttributeError.interdependents_loop_table_top")
                path_mid = rc.translate("native.AttributeError.interdependents_loop_table_mid")
                path_low = rc.translate("native.AttributeError.interdependents_loop_table_low")
                for i, frame in enumerate(loop):
                    path_table = path_top if i == 0 else path_mid if i < len(loop) - 1 else path_low
                    path += f"{path_table}{frame.filename}\n"
                yield rc.translate("native.AttributeError.interdependents_with_loop", obj=self.obj_module_name, attr=attr_rawname, path=path)
                return
            else:
                yield rc.translate("native.AttributeError.interdependents_no_info", obj=self.obj_module_name, attr=attr_rawname)
            return


        if self.wrong_name.startswith('__') and self.wrong_name.endswith('__'):
            wrong_usage_type = "DU"

        candidate_vars: dict[VarsGroup, list] = {"UC": [], "UP": [], "RC": [], "RP": [], "DU": []}
        for name in candidates:
            if not hasattr(self.obj, name):
                continue

            attr = getattr(self.obj, name)
            is_callable = callable(attr)
            is_private = name.startswith('_')
            is_dunder = name.startswith('__') and name.endswith('__')

            if is_dunder:
                candidate_vars["DU"].append(name)
            elif is_private:
                if is_callable:
                    candidate_vars["RC"].append(name)
                else:
                    candidate_vars["RP"].append(name)
            else:
                if is_callable:
                    candidate_vars["UC"].append(name)
                else:
                    candidate_vars["UP"].append(name)

        if wrong_usage_type != "DU" and not any((candidate_vars[t] for t in ("UC", "UP", "RC", "RP"))):  # noqa
            yield rc.translate("native.AttributeError.no_any_prop")
            return

        all_suggestions = find_weighted_closest_matches(self.wrong_name, candidate_vars)
        if all_suggestions[wrong_usage_type]:
            suggestions = [all_suggestions[wrong_usage_type][0]]
            if wrong_usage_type == "UP" and all_suggestions["UC"]:
                if all_suggestions["UP"][0][0] > all_suggestions["UC"][0][0]:
                    # print(f"{all1_suggestions["UP"][0][1]}={all_suggestions["UP"][0][0]}, {all_suggestions["UC"][0][1]}={all_suggestions["UC"][0][0]}")
                    suggestions.append(all_suggestions["UC"][0])
        else:
            suggestions = merge_sorted_suggestions(all_suggestions)[1]

        max_len = rc.translate("native.AttributeError.max_suggest_list")
        if len(suggestions) == 0:  # 没有针对性的建议，只能列出所有属性
            suggest_key = ("native.AttributeError.list_all_property", "native.AttributeError.list_all_callable") \
                [int("C" in wrong_usage_type)]
            suggesting = (
                candidate_vars["UC"] if wrong_usage_type == "UC" else
                candidate_vars["UP"] if wrong_usage_type == "UP" else
                candidate_vars["RC"] + candidate_vars["UC"] if wrong_usage_type == "RC" else
                candidate_vars["RP"] + candidate_vars["UP"] if wrong_usage_type == "RP" else
                candidate_vars["DU"]
            )
            extra = ', ...' if len(suggesting) > max_len else ''
            suggest_all = ', '.join(f"'{word}'" for word in suggesting[:max_len])

            suggestion_line = rc.translate("native.AttributeError.premsg",
                                           obj=obj_rawname,
                                           type_=self.obj_type,
                                           name=attr_rawname) + (
                rc.translate(suggest_key, all=suggest_all, extra=extra)
            )
        else:  # 有针对性的建议，即修改笔误
            extra = ', ...' if len(suggestions) > max_len else ''
            suggest_str = ', '.join(f"'{word}'" for _, word in suggestions[:max_len])
            suggestion_line = rc.translate("native.AttributeError.premsg",
                                           obj=obj_rawname,
                                           type_=self.obj_type,
                                           name=attr_rawname
                                           ) + (
                rc.translate("native.AttributeError.single_suggest", suggest=suggest_str) if len(suggestions) == 1 else
                rc.translate("native.AttributeError.multiple_suggest", suggest=suggest_str) if 1 < len(suggestions) <= 3 else
                rc.translate("native.AttributeError.many_suggest", suggest=suggest_str) if len(suggestions) > 3 else
                rc.translate("native.AttributeError.no_suggest")  # should never reach here
            )

        yield rc.exc_line("AttributeError", suggestion_line)
