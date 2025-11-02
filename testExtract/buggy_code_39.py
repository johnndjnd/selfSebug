def prime_fib(n: int):
    import math

    def is_prime(p):
        if p < 2:
            return False
        for k in range(2, min(int(math.sqrt(p)), p)):
            if p % k == 0:
                return False
        return True
    f = [0, 1]
    while True:
        f.append(f[-1] + f[-2])
        if is_prime(f[-1]):
            n -= 1
        if n == 0:
            return f[-1]


def prime_fib(n: int):
    import math
    def is_prime(p):
        x1 = p < 2
        if x1:
            return False
        x2 = math.sqrt(p)
        x3 = int(x2)
        x4 = min(x3, p)
        x5 = range(2, x4)
        for k in x5:
            x6 = p % k
            x7 = x6 == 0
            if x7:
                return False
        return True
    f = [0, 1]
    while True:
        if not True:
            break
        x9 = -1
        x10 = f[x9]
        x11 = -2
        x12 = f[x11]
        x13 = x10 + x12
        f.append(x13)
        x14 = -1
        x15 = f[x14]
        x16 = is_prime(x15)
        if x16:
            n = n - 1
        x17 = n == 0
        if x17:
            x18 = -1
            x19 = f[x18]
            return x19