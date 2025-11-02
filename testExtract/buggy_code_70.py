def strange_sort_list(lst):
    res, switch = [], False
    while lst:
        res.append(min(lst) if switch else max(lst))
        lst.remove(res[-1])
        switch = not switch
    return res


def strange_sort_list(lst):
    x1 = []
    x2 = (x1, False)
    res, switch = x2
    while True:
        if not lst:
            break
        x3 = min(lst)
        x4 = max(lst)
        x5 = x3 if switch else x4
        res.append(x5)
        x6 = -1
        x7 = res[x6]
        lst.remove(x7)
        switch = not switch
    return res