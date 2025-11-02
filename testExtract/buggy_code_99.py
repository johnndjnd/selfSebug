def closest_integer(value):
    from math import floor, ceil

    if value.count('.') == 1:
        # remove trailing zeros
        while (value[-1] == '0'):
            value = value[:-1]

    num = float(value)
    if value[-2:] == '.5':
        if num > 0:
            res = floor(num)
        else:
            res = ceil(num)
    elif len(value) > 0:
        res = int(round(num))
    else:
        res = 0

    return res



def closest_integer(value):
    from math import floor, ceil
    x1 = value.count('.')
    x2 = x1 == 1
    if x2:
        while True:
            x3 = -1
            x4 = value[x3]
            x5 = x4 == '0'
            if not x5:
                break
            value = value[:-1]
    num = float(value)
    x8 = value[-2:]
    x9 = x8 == '.5'
    if x9:
        x10 = num > 0
        if x10:
            res = floor(num)
        else:
            res = ceil(num)
    else:
        x13 = len(value)
        x14 = x13 > 0
        if x14:
            x15 = round(num)
            res = int(x15)
        else:
            res = 0
    return res