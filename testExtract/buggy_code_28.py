from typing import List


def concatenate(strings: List[str]) -> str:
    return ' '.join(strings)


from typing import List   # 未分解语句
def concatenate(strings: List[str]):
    x1 = ' '.join(strings)
    return x1