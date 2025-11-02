from typing import List


def filter_by_prefix(strings: List[str], prefix: str) -> List[str]:
    return [x for x in strings if x.endswith(prefix)]


from typing import List   # 未分解语句
def filter_by_prefix(strings: List[str], prefix: str):
    x1 = []
    for x in strings:
        x2 = x.endswith(prefix)
        if x2:
            x1.append(x)
    return x1