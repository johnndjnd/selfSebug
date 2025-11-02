def get_row(lst, x):
    coords = [(j, i) for i in range(len(lst)) for j in range(len(lst[i])) if lst[i][j] == x]
    return sorted(sorted(coords, key=lambda x: x[1], reverse=True), key=lambda x: x[0])


def get_row(lst, x):
    x1 = []
    x2 = len(lst)
    x3 = range(x2)
    for i in x3:
        x4 = (j, i)
        x1.append(x4)
    coords = x1
    x5 = lambda x: x[1]
    x6 = sorted(coords, key=x5, reverse=True)
    x7 = lambda x: x[0]
    x8 = sorted(x6, key=x7)
    return x8