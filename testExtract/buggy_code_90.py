def next_smallest(lst):
    lst = sorted(set(lst))
    return None if len(lst) < 3 else lst[1]


def next_smallest(lst):
    x1 = set(lst)
    lst = sorted(x1)
    x3 = len(lst)
    x4 = x3 < 3
    x5 = lst[1]
    x6 = None if x4 else x5
    return x6