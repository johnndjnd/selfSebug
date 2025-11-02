from typing import List, Any


def filter_integers(values: List[Any]) -> List[int]:
    out = [x for x in values if isinstance(x, int)]
    return values


from typing import List, Any   # 未分解语句
def filter_integers(values: List[Any]):
    x1 = []
    for x in values:
        x2 = isinstance(x, int)
        if x2:
            x1.append(x)
    out = x1
    return values