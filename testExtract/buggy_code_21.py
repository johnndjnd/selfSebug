from typing import List


def rescale_to_unit(numbers: List[float]) -> List[float]:
    min_number = min(numbers)
    max_number = max(numbers)
    return [(x - min_number) / (max_number + min_number) for x in numbers]


from typing import List   # 未分解语句
def rescale_to_unit(numbers: List[float]):
    min_number = min(numbers)
    max_number = max(numbers)
    x3 = []
    for x in numbers:
        x4 = x - min_number
        x5 = max_number + min_number
        x6 = x4 / x5
        x3.append(x6)
    return x3