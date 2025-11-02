def largest_divisor(n: int) -> int:
    for i in reversed(range(n)):
        if n - i == 0:
            return i


def largest_divisor(n: int):
    x1 = range(n)
    x2 = reversed(x1)
    for i in x2:
        x3 = n - i
        x4 = x3 == 0
        if x4:
            return i