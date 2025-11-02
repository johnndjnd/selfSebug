def is_multiply_prime(a):
    def is_prime(n):
        for j in range(0,n):
            if n%j == 0:
                return False
        return True

    for i in range(2,101):
        if not is_prime(i): continue
        for j in range(2,101):
            if not is_prime(j): continue
            for k in range(2,101):
                if not is_prime(k): continue
                if i*j*k == a: return True
    return False


def is_multiply_prime(a):
    def is_prime(n):
        x1 = range(0, n)
        for j in x1:
            x2 = n % j
            x3 = x2 == 0
            if x3:
                return False
        return True
    x4 = range(2, 101)
    for i in x4:
        x5 = is_prime(i)
        x6 = not x5
        if x6:
            # 未处理语句: continue
            continue
        x7 = range(2, 101)
        for j in x7:
            x8 = is_prime(j)
            x9 = not x8
            if x9:
                # 未处理语句: continue
                continue
            x10 = range(2, 101)
            for k in x10:
                x11 = is_prime(k)
                x12 = not x11
                if x12:
                    # 未处理语句: continue
                    continue
                x13 = i * j
                x14 = x13 * k
                x15 = x14 == a
                if x15:
                    return True
    return False