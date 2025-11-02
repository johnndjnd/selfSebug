from typing import List


def intersperse(numbers: List[int], delimeter: int) -> List[int]:
    if not numbers:
        return []

    result = []

    for n in numbers[:-1]:
        result.append(n)
        result.append(delimeter)

    return result


from typing import List   # 未分解语句
def intersperse(numbers: List[int], delimeter: int):
    x1 = not numbers
    if x1:
        x2 = []
        return x2
    result = []
    x4 = numbers[:-1]
    for n in x4:
        result.append(n)
        result.append(delimeter)
    return result