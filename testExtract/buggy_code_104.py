def unique_digits(x):
    odd_digit_elements = []
    for j, i in enumerate(x):
        if all (int(c) % 2 == 1 for c in str(i)):
            odd_digit_elements.append(i)
            odd_digit_elements.append(j)
    return sorted(odd_digit_elements)


def unique_digits(x):
    odd_digit_elements = []
    x2 = enumerate(x)
    for j, i in x2:
        x3 = []
        x4 = str(i)
        for c in x4:
            x5 = int(c)
            x6 = x5 % 2
            x7 = x6 == 1
            x3.append(x7)
        x9 = (x8 for x8 in x3)
        x10 = all(x9)
        if x10:
            odd_digit_elements.append(i)
            odd_digit_elements.append(j)
    x11 = sorted(odd_digit_elements)
    return x11