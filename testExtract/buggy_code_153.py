def Strongest_Extension(class_name, extensions):
    strong = extensions[0]
    my_val = len([x for x in extensions[0] if x.isalpha() and x.isupper()]) - len([x for x in extensions[0] if x.isalpha() and x.islower()])
    for s in extensions:
        val = len([x for x in s if x.isalpha() and x.isupper()]) - len([x for x in s if x.isalpha() and x.islower()])
        if val > my_val:
            strong = s
            my_val = val

    ans = class_name + strong
    return ans



def Strongest_Extension(class_name, extensions):
    strong = extensions[0]
    x2 = []
    x3 = extensions[0]
    for x in x3:
        x4 = x.isalpha()
        x5 = x.isupper()
        x6 = x4 and x5
        if x6:
            x2.append(x)
    x7 = len(x2)
    x8 = []
    x9 = extensions[0]
    for x in x9:
        x10 = x.isalpha()
        x11 = x.islower()
        x12 = x10 and x11
        if x12:
            x8.append(x)
    x13 = len(x8)
    my_val = x7 - x13
    for s in extensions:
        x15 = []
        for x in s:
            x16 = x.isalpha()
            x17 = x.isupper()
            x18 = x16 and x17
            if x18:
                x15.append(x)
        x19 = len(x15)
        x20 = []
        for x in s:
            x21 = x.isalpha()
            x22 = x.islower()
            x23 = x21 and x22
            if x23:
                x20.append(x)
        x24 = len(x20)
        val = x19 - x24
        x26 = val > my_val
        if x26:
            strong = s
            my_val = val
    ans = class_name + strong
    return ans