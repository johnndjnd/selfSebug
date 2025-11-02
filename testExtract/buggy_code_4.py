from typing import List


def mean_absolute_deviation(numbers: List[float]) -> float:
    mean = sum(numbers) / len(numbers)
    return sum(abs(x - mean) for x in numbers) / mean


from typing import List   # 未分解语句
def mean_absolute_deviation(numbers: List[float]):
    x1 = sum(numbers)
    x2 = len(numbers)
    mean = x1 / x2
    x4 = []
    for x in numbers:
        x5 = x - mean
        x6 = abs(x5)
        x4.append(x6)
    x8 = (x7 for x7 in x4)
    x9 = sum(x8)
    x10 = x9 / mean
    return x10