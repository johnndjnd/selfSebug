from typing import List


def factorize(n: int) -> List[int]:
    import math
    fact = []
    i = 0
    while i <= int(math.sqrt(n) + 1):
        if n % i == 0:
            fact.append(i)
            n //= i
        else:
            i += 1

    if n > 1:
        fact.append(n)
    return fact


from typing import List   # 未分解语句
def factorize(n: int):
    import math
    fact = []
    i = 0
    while True:
        x2 = math.sqrt(n)
        x3 = x2 + 1
        x4 = int(x3)
        x5 = i <= x4
        if not x5:
            break
        x6 = n % i
        x7 = x6 == 0
        if x7:
            fact.append(i)
            n = n // i
        else:
            i = i + 1
    x8 = n > 1
    if x8:
        fact.append(n)
    return fact