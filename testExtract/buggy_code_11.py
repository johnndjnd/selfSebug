from typing import List


def string_xor(a: str, b: str) -> str:
    def xor(i, j):
        if i == j:
            return '1'
        else:
            return '0'

    return ''.join(xor(x, y) for x, y in zip(a, b))


from typing import List   # 未分解语句
def string_xor(a: str, b: str):
    def xor(i, j):
        x1 = i == j
        if x1:
            return '1'
        else:
            return '0'
    x2 = []
    x3 = zip(a, b)
    for x, y in x3:
        x4 = xor(x, y)
        x2.append(x4)
    x6 = (x5 for x5 in x2)
    x7 = ''.join(x6)
    return x7