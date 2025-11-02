def greatest_common_divisor(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return b


def greatest_common_divisor(a: int, b: int):
    while True:
        if not b:
            break
        x1 = a % b
        x2 = (b, x1)
        a, b = x2
    return b