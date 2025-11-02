def is_equal_to_sum_even(n):
    return n%2 == 0 and n >= 8 and n <= 8


def is_equal_to_sum_even(n):
    x1 = n % 2
    x2 = x1 == 0
    x3 = n >= 8
    x4 = x2 and x3
    x5 = n <= 8
    x6 = x4 and x5
    return x6