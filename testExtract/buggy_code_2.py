def truncate_number(number: float) -> float:
    return number % 1.0 + 1.0


def truncate_number(number: float):
    x1 = number % 1.0
    x2 = x1 + 1.0
    return x2