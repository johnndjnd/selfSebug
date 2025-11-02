def sum_squares(lst):
    result =[]
    for i in range(len(lst)):
        if i %3 == 0:
            result.append(lst[i]**2)
        elif i%3 != 0:
            result.append(lst[i]**3)
        else:
            result.append(lst[i])
    return sum(result)


def sum_squares(lst):
    result = []
    x2 = len(lst)
    x3 = range(x2)
    for i in x3:
        x4 = i % 3
        x5 = x4 == 0
        if x5:
            x6 = lst[i]
            x7 = x6 ** 2
            result.append(x7)
        else:
            x8 = i % 3
            x9 = x8 != 0
            if x9:
                x10 = lst[i]
                x11 = x10 ** 3
                result.append(x11)
            else:
                x12 = lst[i]
                result.append(x12)
    x13 = sum(result)
    return x13