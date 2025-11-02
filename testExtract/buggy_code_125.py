def split_words(txt):
    if " " in txt:
        return txt.split()
    elif "," in txt:
        return txt.replace(' ',',').split()
    else:
        return len([i for i in txt if i.islower() and ord(i)%2 == 0])


def split_words(txt):
    x1 = " " in txt
    if x1:
        x2 = txt.split()
        return x2
    else:
        x3 = "," in txt
        if x3:
            x4 = txt.replace(' ', ',')
            x5 = x4.split()
            return x5
        else:
            x6 = []
            for i in txt:
                x7 = i.islower()
                x8 = ord(i)
                x9 = x8 % 2
                x10 = x9 == 0
                x11 = x7 and x10
                if x11:
                    x6.append(i)
            x12 = len(x6)
            return x12