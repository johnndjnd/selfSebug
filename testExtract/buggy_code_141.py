def file_name_check(file_name):
    suf = ['txt', 'exe', 'dll']
    lst = file_name.split(sep='.')
    if len(lst) != 2:
        return 'No'
    if len(lst[0]) == 0:
        return 'No'
    if not lst[0][0].isalpha():
        return 'No'
    t = len([x for x in lst[0] if x.isdigit()])
    if t > 3:
        return 'No'
    return 'Yes'


def file_name_check(file_name):
    suf = ['txt', 'exe', 'dll']
    lst = file_name.split(sep='.')
    x3 = len(lst)
    x4 = x3 != 2
    if x4:
        return 'No'
    x5 = lst[0]
    x6 = len(x5)
    x7 = x6 == 0
    if x7:
        return 'No'
    x8 = lst[0]
    x9 = x8[0]
    x10 = x9.isalpha()
    x11 = not x10
    if x11:
        return 'No'
    x12 = []
    x13 = lst[0]
    for x in x13:
        x14 = x.isdigit()
        if x14:
            x12.append(x)
    t = len(x12)
    x16 = t > 3
    if x16:
        return 'No'
    return 'Yes'