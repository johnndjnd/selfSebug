def cycpattern_check(a , b):
    l = len(b)
    pat = b + b
    for i in range(len(a) - l + 1):
        for j in range(len(b) - l + 1):
            if a[i:i+l] == pat[j:j+l]:
                return True
    return False


def cycpattern_check(a , b):
    l = len(b)
    pat = b + b
    x3 = len(a)
    x4 = x3 - l
    x5 = x4 + 1
    x6 = range(x5)
    for i in x6:
        x7 = len(b)
        x8 = x7 - l
        x9 = x8 + 1
        x10 = range(x9)
        for j in x10:
            x11 = i + l
            x12 = a[i:x11]
            x13 = j + l
            x14 = pat[j:x13]
            x15 = x12 == x14
            if x15:
                return True
    return False