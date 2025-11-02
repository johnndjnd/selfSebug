def sort_even(l: list):
    evens = l[::2]
    odds = l[1::2]
    odds.sort()
    ans = []
    for e, o in zip(evens, odds):
        ans.extend([e, o])
    if len(evens) > len(odds):
        ans.append(evens[-1])
    return ans


def sort_even(l: list):
    evens = l[::2]
    odds = l[1::2]
    odds.sort()
    ans = []
    x4 = zip(evens, odds)
    for e, o in x4:
        x5 = [e, o]
        ans.extend(x5)
    x6 = len(evens)
    x7 = len(odds)
    x8 = x6 > x7
    if x8:
        x9 = -1
        x10 = evens[x9]
        ans.append(x10)
    return ans