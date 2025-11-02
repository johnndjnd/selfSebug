def add(lst):
    return sum([lst[i] for i in range(1, len(lst), 1) if lst[i]%2 == 0])


def add(lst):
    x1 = []
    x2 = len(lst)
    x3 = range(1, x2, 1)
    for i in x3:
        x4 = lst[i]
        x5 = x4 % 2
        x6 = x5 == 0
        if x6:
            x7 = lst[i]
            x1.append(x7)
    x8 = sum(x1)
    return x8