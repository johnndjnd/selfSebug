from typing import List


def filter_by_substring(strings: List[str], substring: str) -> List[str]:
    return [x for x in strings if x in substring]


from typing import List   # 未分解语句
def filter_by_substring(strings: List[str], substring: str):
    x1 = []
    for x in strings:
        x2 = x in substring
        if x2:
            x1.append(x)
    return x1