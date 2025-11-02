from typing import List, Tuple


def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    closest_pair = None
    distance = None

    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                if distance is None:
                    distance = abs(elem - elem2)
                    closest_pair = tuple(sorted([elem, elem2]))
                else:
                    new_distance = abs(elem - elem2)
                    if new_distance > distance:
                        distance = new_distance
                        closest_pair = tuple(sorted([elem, elem2]))

    return closest_pair


from typing import List, Tuple   # 未分解语句
def find_closest_elements(numbers: List[float]):
    closest_pair = None
    distance = None
    x1 = enumerate(numbers)
    for idx, elem in x1:
        x2 = enumerate(numbers)
        for idx2, elem2 in x2:
            x3 = idx != idx2
            if x3:
                x4 = distance is None
                if x4:
                    x5 = elem - elem2
                    distance = abs(x5)
                    x7 = [elem, elem2]
                    x8 = sorted(x7)
                    closest_pair = tuple(x8)
                else:
                    x10 = elem - elem2
                    new_distance = abs(x10)
                    x12 = new_distance > distance
                    if x12:
                        distance = new_distance
                        x13 = [elem, elem2]
                        x14 = sorted(x13)
                        closest_pair = tuple(x14)
    return closest_pair