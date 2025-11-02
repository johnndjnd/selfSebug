def order_by_points(nums):
    def digits_sum(n):
        neg = 1
        if n < 0: n, neg = -1 * n, -1 + n 
        n = [int(i) for i in str(n)]
        n[0] = n[0] * neg
        return sum(n)
    return sorted(nums, key=digits_sum)


def order_by_points(nums):
    def digits_sum(n):
        neg = 1
        x1 = n < 0
        if x1:
            x2 = -1
            x3 = x2 * n
            x4 = -1
            x5 = x4 + n
            x6 = (x3, x5)
            n, neg = x6
        x7 = []
        x8 = str(n)
        for i in x8:
            x9 = int(i)
            x7.append(x9)
        n = x7
        x10 = n[0]
        x11 = x10 * neg
        n[0] = x11
        x12 = sum(n)
        return x12
    x13 = sorted(nums, key=digits_sum)
    return x13