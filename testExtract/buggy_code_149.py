def sorted_list_sum(lst):
    lst.sort()
    new_lst = []
    for i in lst:
        if len(i)%2 == 0:
            new_lst.append(i)
    return new_lst


def sorted_list_sum(lst):
    lst.sort()
    new_lst = []
    for i in lst:
        x2 = len(i)
        x3 = x2 % 2
        x4 = x3 == 0
        if x4:
            new_lst.append(i)
    return new_lst