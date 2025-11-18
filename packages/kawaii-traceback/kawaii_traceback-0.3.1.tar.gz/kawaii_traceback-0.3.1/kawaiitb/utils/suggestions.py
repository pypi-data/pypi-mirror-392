import sys
from typing import Collection, Literal

_MAX_CANDIDATE_ITEMS = 750
_MAX_STRING_SIZE = 40
_MOVE_COST = 1
_CASE_COST = 1

VarsGroup = Literal["UC", "UP", "RC", "RP", "DU"]


_SUBSTITUTE_COST = 1
_TRANSPOSE_COST = 1


def osa_distance(a, b, max_cost=sys.maxsize):
    """Compute the Optimal String Alignment (OSA) distance between strings a and b.

    This is similar to Damerau-Levenshtein but doesn't allow multiple edits on substrings.
    """
    # Both strings are the same
    if a == b:
        return 0

    # Trim away common affixes
    pre = 0
    while a[pre:] and b[pre:] and a[pre] == b[pre]:
        pre += 1
    a = a[pre:]
    b = b[pre:]
    post = 0
    while a[:post or None] and b[:post or None] and a[post - 1] == b[post - 1]:
        post -= 1
    a = a[:post or None]
    b = b[:post or None]
    if not a or not b:
        return min(_MOVE_COST * (len(a) + len(b)), max_cost + 1)
    if len(a) > _MAX_STRING_SIZE or len(b) > _MAX_STRING_SIZE:
        return max_cost + 1

    # Initialize distance matrix
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]

    # Initialize first row and column
    for i in range(len(a) + 1):
        d[i][0] = i * _MOVE_COST
    for j in range(len(b) + 1):
        d[0][j] = j * _MOVE_COST

    # Fill the distance matrix
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else _SUBSTITUTE_COST

            d[i][j] = min(
                d[i - 1][j] + _MOVE_COST,  # deletion
                d[i][j - 1] + _MOVE_COST,  # insertion
                d[i - 1][j - 1] + cost  # substitution
            )

            # Check for transposition
            if (i > 1 and j > 1 and
                    a[i - 1] == b[j - 2] and
                    a[i - 2] == b[j - 1]):
                d[i][j] = min(
                    d[i][j],
                    d[i - 2][j - 2] + _TRANSPOSE_COST
                )

            # Early exit if we've exceeded max_cost
            if d[i][j] > max_cost:
                return max_cost + 1

    return min(d[len(a)][len(b)], max_cost + 1)


def find_closest_matches(wrong_name: str,
                         candidates: Collection[str],
                         max_items: int=_MAX_CANDIDATE_ITEMS,
                         max_distance: int=None) -> list[tuple[int, str]]:
    """从候选词中找出与目标词最接近的匹配项

    Args:
        wrong_name: 要匹配的目标词
        candidates: 候选词列表
        max_items: 最大候选词数量限制
        max_distance: 最大允许的编辑距离(为None时使用1/3名称长度)

    Returns:
        一个按距离排序的列表
        例如：[(1, 'typo'), (3, 'typing')]
    """
    if len(candidates) > max_items:
        return []

    wrong_name_len = len(wrong_name)
    if wrong_name_len > _MAX_STRING_SIZE:
        return []

    if max_distance is None:
        # 默认计算最大允许距离
        max_distance = (len(wrong_name) + 3) * _MOVE_COST // 3

    matches = []
    for candidate in candidates:
        if candidate == wrong_name:
            continue

        distance = osa_distance(wrong_name, candidate, max_distance)
        if distance <= max_distance:
            matches.append((distance, candidate))

    # 按距离排序并返回
    return sorted(matches, key=lambda x: x[0])


def merge_sorted_suggestions(suggestions_groups: dict[str, list[tuple[int, str]]],
                             if_only_group: str=None) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """合并多个有序建议列表

    Args:
        suggestions_groups: 多个已排序的建议列表
        if_only_group: 如果存在，则将本组和其他组的建议分离返回

    Returns:
        if-only组列表与合并后的有序建议列表
    """
    import heapq

    # 将每个列表转换为迭代器
    iters = [iter(group) for type_, group in suggestions_groups.items() if if_only_group != type_]
    # 初始化堆，取每个列表的第一个元素
    heap = []
    for i, it in enumerate(iters):
        try:
            item = next(it)
            heapq.heappush(heap, (item[0], i, item[1]))
        except StopIteration:
            pass

    # 合并排序
    merged_suggestions = []
    while heap:
        score, i, name = heapq.heappop(heap)
        merged_suggestions.append((score, name))
        try:
            next_item = next(iters[i])
            heapq.heappush(heap, (next_item[0], i, next_item[1]))
        except StopIteration:
            pass

    if if_only_group:
        return suggestions_groups[if_only_group], merged_suggestions
    else:
        return [], merged_suggestions


def find_weighted_closest_matches(wrong_name: str,
                                  candidate_vars: dict[VarsGroup, Collection[str]]) -> dict[str, list[tuple[int, str]]]:
    """从候选变量中找出与目标变量最接近的匹配项
    Args:
        wrong_name: 要匹配的目标变量名
        candidate_vars: 候选变量列表
    Returns:
        与目标变量同类别的候选变量列表和其他合并后的有序建议列表
    """
    suggestions_groups: dict[str, list[tuple[int, str]]] = {}
    for candidate_type, candidates in candidate_vars.items():
        suggestions = find_closest_matches(wrong_name, candidates)
        suggestions_groups[candidate_type] = suggestions
    return suggestions_groups

if __name__ == "__main__":
    # sqr 与 sqrt 的距离
    # sqr 与 sin 的距离
    print(osa_distance("sqr", "sqrt")) # 2
    print(osa_distance("sqr", "sin")) # 2

    # 为什么都是2？为什么插入消费是2？

