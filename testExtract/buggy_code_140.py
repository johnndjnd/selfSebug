def fix_spaces(text):
    new_text = ""
    i = 0
    start, end = 0, 0
    while i < len(text):
        if text[i] == " ":
            end += 1
        else:
            if end - start > 2:
                new_text += "-"+text[i]
            elif end - start > 0:
                new_text += "_"*(end - start)+text[i]
            else:
                new_text += text[i]
            start, end = i+1, i+1
        i+=1
    if end - start > 2:
        new_text += "-"
    elif end - start > 0:
        new_text += "__"
    return new_text


def fix_spaces(text):
    new_text = ""
    i = 0
    x1 = (0, 0)
    start, end = x1
    while True:
        x2 = len(text)
        x3 = i < x2
        if not x3:
            break
        x4 = text[i]
        x5 = x4 == " "
        if x5:
            end = end + 1
        else:
            x6 = end - start
            x7 = x6 > 2
            if x7:
                x8 = text[i]
                x9 = "-" + x8
                new_text = new_text + x9
            else:
                x10 = end - start
                x11 = x10 > 0
                if x11:
                    x12 = end - start
                    x13 = "_" * x12
                    x14 = text[i]
                    x15 = x13 + x14
                    new_text = new_text + x15
                else:
                    x16 = text[i]
                    new_text = new_text + x16
            x17 = i + 1
            x18 = i + 1
            x19 = (x17, x18)
            start, end = x19
        i = i + 1
    x20 = end - start
    x21 = x20 > 2
    if x21:
        new_text = new_text + "-"
    else:
        x22 = end - start
        x23 = x22 > 0
        if x23:
            new_text = new_text + "__"
    return new_text