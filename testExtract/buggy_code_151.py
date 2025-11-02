def double_the_difference(lst):
    return sum([i**2 for i in lst if i > 0 and "." not in str(i)])


def double_the_difference(lst):
    x1 = []
    for i in lst:
        x2 = i > 0
        x3 = str(i)
        x4 = "." not in x3
        x5 = x2 and x4
        if x5:
            x6 = i ** 2
            x1.append(x6)
    x7 = sum(x1)
    return x7