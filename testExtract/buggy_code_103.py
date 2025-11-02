def rounded_avg(n, m):
    if m < n:
        return -1
    summation = 0
    for i in range(n, m+1):
        summation += i
    return bin(round(summation/(m - n)))


def rounded_avg(n, m):
    x1 = m < n
    if x1:
        x2 = -1
        return x2
    summation = 0
    x3 = m + 1
    x4 = range(n, x3)
    for i in x4:
        summation = summation + i
    x5 = m - n
    x6 = summation / x5
    x7 = round(x6)
    x8 = bin(x7)
    return x8