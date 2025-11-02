def eat(number, need, remaining):
    if(need <= remaining):
        return [ number + need , number + remaining-need ]
    else:
        return [ number + need + remaining , 0]


def eat(number, need, remaining):
    x1 = need <= remaining
    if x1:
        x2 = number + need
        x3 = number + remaining
        x4 = x3 - need
        x5 = [x2, x4]
        return x5
    else:
        x6 = number + need
        x7 = x6 + remaining
        x8 = [x7, 0]
        return x8