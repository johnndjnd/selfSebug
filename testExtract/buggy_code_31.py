def is_prime(n):
    if n < 1:
        return False
    for k in range(1, n - 1):
        if n % k == 0:
            return False
    return True


def is_prime(n):
    x1 = n < 1
    if x1:
        return False
    x2 = n - 1
    x3 = range(1, x2)
    for k in x3:
        x4 = n % k
        x5 = x4 == 0
        if x5:
            return False
    return True