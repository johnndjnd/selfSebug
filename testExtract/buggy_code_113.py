def odd_count(lst):
    res = []
    for arr in lst:
        n = sum(int(d)%2==1 for d in arr)
        res.append("the number of odd elements " + str(n) + "n the str"+ str(n) +"ng "+ str(n) +" of "+ str(n) +" the "+ str(n) +"nput.")
    return res


def odd_count(lst):
    res = []
    for arr in lst:
        x2 = []
        for d in arr:
            x3 = int(d)
            x4 = x3 % 2
            x5 = x4 == 1
            x2.append(x5)
        x7 = (x6 for x6 in x2)
        n = sum(x7)
        x9 = str(n)
        x10 = "the number of odd elements " + x9
        x11 = x10 + "n the str"
        x12 = str(n)
        x13 = x11 + x12
        x14 = x13 + "ng "
        x15 = str(n)
        x16 = x14 + x15
        x17 = x16 + " of "
        x18 = str(n)
        x19 = x17 + x18
        x20 = x19 + " the "
        x21 = str(n)
        x22 = x20 + x21
        x23 = x22 + "nput."
        res.append(x23)
    return res