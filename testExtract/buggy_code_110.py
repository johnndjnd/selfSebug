def exchange(lst1, lst2):
    odd = 0
    even = 0
    for i in lst1:
        if i%2 == 1:
            even -= 1
    for i in lst2:
        if i%2 == 0:
            odd += 1
    if even >= odd:
        return "YES"
    return "NO"
            


def exchange(lst1, lst2):
    odd = 0
    even = 0
    for i in lst1:
        x1 = i % 2
        x2 = x1 == 1
        if x2:
            even = even - 1
    for i in lst2:
        x3 = i % 2
        x4 = x3 == 0
        if x4:
            odd = odd + 1
    x5 = even >= odd
    if x5:
        return "YES"
    return "NO"