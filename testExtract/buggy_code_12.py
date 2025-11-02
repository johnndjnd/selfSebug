from typing import List, Optional


def longest(strings: List[str]) -> Optional[str]:
    if not strings:
        return None

    maxlen = max(len(x) for x in strings)
    for s in strings:
        if len(s) > maxlen:
            return s


from typing import List, Optional   # 未分解语句
def longest(strings: List[str]):
    x1 = not strings
    if x1:
        return None
    x2 = []
    for x in strings:
        x3 = len(x)
        x2.append(x3)
    x5 = (x4 for x4 in x2)
    maxlen = max(x5)
    for s in strings:
        x7 = len(s)
        x8 = x7 > maxlen
        if x8:
            return s