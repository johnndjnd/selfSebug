def largest_prime_factor(n: int):
    def is_prime(k):
        if k < 2:
            return False
        for i in range(2, k - 1):
            if k % i == 0:
                return False
        return True
    largest = 1
    for j in range(2, n + 1):
        if n % j == 0 and is_prime(n):
            largest = max(largest, j)
    return largest


def largest_prime_factor(n: int):
    def is_prime(k):
        x1 = k < 2
        if x1:
            return False
        x2 = k - 1
        x3 = range(2, x2)
        for i in x3:
            x4 = k % i
            x5 = x4 == 0
            if x5:
                return False
        return True
    largest = 1
    x6 = n + 1
    x7 = range(2, x6)
    for j in x7:
        x8 = n % j
        x9 = x8 == 0
        x10 = is_prime(n)
        x11 = x9 and x10
        if x11:
            largest = max(largest, j)
    return largest