def tri(n):
    if n == 0:
        return [1]
    my_tri = [1, 3]
    for i in range(2, n + 1):
        if i % 2 == 0:
            my_tri.append(i / 2 + 1)
        else:
            my_tri.append(my_tri[i - 1] + my_tri[i - 2] + i + (i + 3) / 2)
    return my_tri


def tri(n):
    x1 = n == 0
    if x1:
        x2 = [1]
        return x2
    my_tri = [1, 3]
    x4 = n + 1
    x5 = range(2, x4)
    for i in x5:
        x6 = i % 2
        x7 = x6 == 0
        if x7:
            x8 = i / 2
            x9 = x8 + 1
            my_tri.append(x9)
        else:
            x10 = i - 1
            x11 = my_tri[x10]
            x12 = i - 2
            x13 = my_tri[x12]
            x14 = x11 + x13
            x15 = x14 + i
            x16 = i + 3
            x17 = x16 / 2
            x18 = x15 + x17
            my_tri.append(x18)
    return my_tri