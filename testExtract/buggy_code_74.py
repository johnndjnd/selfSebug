def total_match(lst1, lst2):
    l1 = 0
    for st in lst1:
        l1 += len(st)
    
    l2 = 0
    for st in lst2:
        l2 += len(st)
    
    if l1 <= l2:
        return lst2
    else:
        return lst1


def total_match(lst1, lst2):
    l1 = 0
    for st in lst1:
        x1 = len(st)
        l1 = l1 + x1
    l2 = 0
    for st in lst2:
        x2 = len(st)
        l2 = l2 + x2
    x3 = l1 <= l2
    if x3:
        return lst2
    else:
        return lst1