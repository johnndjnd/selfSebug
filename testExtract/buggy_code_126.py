def is_sorted(lst):
    count_digit = dict([(i, 0) for i in lst])
    for i in lst:
        count_digit[i]+=1
    if all(lst[i-1] <= lst[i] for i in range(1, len(lst))):
        return True
    else:
        return False
    
    


def is_sorted(lst):
    x1 = []
    for i in lst:
        x2 = (i, 0)
        x1.append(x2)
    count_digit = dict(x1)
    for i in lst:
        x4 = count_digit[i]
        x4 = x4 + 1
    x5 = []
    x6 = len(lst)
    x7 = range(1, x6)
    for i in x7:
        x8 = i - 1
        x9 = lst[x8]
        x10 = lst[i]
        x11 = x9 <= x10
        x5.append(x11)
    x13 = (x12 for x12 in x5)
    x14 = all(x13)
    if x14:
        return True
    else:
        return False