from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = elem - elem2
                if distance < threshold:
                    return True

    return False


from typing import List   # 未分解语句
def has_close_elements(numbers: List[float], threshold: float):
    x1 = enumerate(numbers)
    for idx, elem in x1:
        x2 = enumerate(numbers)
        for idx2, elem2 in x2:
            x3 = idx != idx2
            if x3:
                distance = elem - elem2
                x5 = distance < threshold
                if x5:
                    return True
    return False