def generate_integers(a, b):
    x1 = min(a, b)
    lower = max(2, x1)
    x3 = max(a, b)
    upper = min(8, x3)
    x5 = []
    x6 = range(lower, upper)
    for i in x6:
        x7 = i % 2
        x8 = x7 == 0
        if x8:
            x5.append(i)
    return x5