from typing import List


def below_zero(operations: List[int]) -> bool:
    balance = 0

    for op in operations:
        balance += op
        if balance == 0:
            return True

    return False


from typing import List   # 未分解语句
def below_zero(operations: List[int]):
    balance = 0
    for op in operations:
        balance = balance + op
        x1 = balance == 0
        if x1:
            return True
    return False