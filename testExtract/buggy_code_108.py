def count_nums(arr):
    def digits_sum(n):
        neg = 1
        if n < 0: n, neg = -1 * n, -1 
        n = [int(i) for i in str(n)]
        n[0] = n[0] * neg * -1
        return sum(n)
    return len(list(filter(lambda x: x > 0, [digits_sum(i) for i in arr])))


def count_nums(arr):
    def digits_sum(n):
        neg = 1
        x1 = n < 0
        if x1:
            x2 = -1
            x3 = x2 * n
            x4 = -1
            x5 = (x3, x4)
            n, neg = x5
        x6 = []
        x7 = str(n)
        for i in x7:
            x8 = int(i)
            x6.append(x8)
        n = x6
        x9 = n[0]
        x10 = x9 * neg
        x11 = -1
        x12 = x10 * x11
        n[0] = x12
        x13 = sum(n)
        return x13
    x14 = lambda x: x > 0
    x15 = []
    for i in arr:
        x16 = digits_sum(i)
        x15.append(x16)
    x17 = filter(x14, x15)
    x18 = list(x17)
    x19 = len(x18)
    return x19