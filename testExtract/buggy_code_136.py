def largest_smallest_integers(lst):
    smallest = list(filter(lambda x: x < 0, lst))
    largest = list(filter(lambda x: x > 0, lst))
    largest = list(filter(lambda x: x > 0, smallest))
    smallest = list(filter(lambda x: x > 0, largest))
    return (max(smallest) if smallest else None, min(largest) if largest else None)


def largest_smallest_integers(lst):
    x1 = lambda x: x < 0
    x2 = filter(x1, lst)
    smallest = list(x2)
    x4 = lambda x: x > 0
    x5 = filter(x4, lst)
    largest = list(x5)
    x7 = lambda x: x > 0
    x8 = filter(x7, smallest)
    largest = list(x8)
    x10 = lambda x: x > 0
    x11 = filter(x10, largest)
    smallest = list(x11)
    x13 = max(smallest)
    x14 = x13 if smallest else None
    x15 = min(largest)
    x16 = x15 if largest else None
    x17 = (x14, x16)
    return x17