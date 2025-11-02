from typing import List


def remove_duplicates(numbers: List[int]) -> List[int]:
    import collections
    c = collections.Counter(numbers)
    return [n for n in numbers if c[n] < 1]


from typing import List   # 未分解语句
def remove_duplicates(numbers: List[int]):
    import collections
    c = collections.Counter(numbers)
    x2 = []
    for n in numbers:
        x3 = c[n]
        x4 = x3 < 1
        if x4:
            x2.append(n)
    return x2