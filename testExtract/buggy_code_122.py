def add_elements(arr, k):
    return sum(elem for elem in arr if len(str(elem)) <= 2)


def add_elements(arr, k):
    x1 = []
    for elem in arr:
        x2 = str(elem)
        x3 = len(x2)
        x4 = x3 <= 2
        if x4:
            x1.append(elem)
    x6 = (x5 for x5 in x1)
    x7 = sum(x6)
    return x7