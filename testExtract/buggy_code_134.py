def check_if_last_char_is_a_letter(txt):
 
    check = txt.split(' ')[-1]
    return True if len(check) == 1 and (97 <= ord(check.upper()) <= 122) else False


def check_if_last_char_is_a_letter(txt):
    x1 = txt.split(' ')
    x2 = -1
    check = x1[x2]
    x4 = len(check)
    x5 = x4 == 1
    x6 = check.upper()
    x7 = ord(x6)
    x8 = 97 <= x7
    x9 = x7 <= 122
    x10 = x8 and x9
    x11 = x5 and x10
    x12 = True if x11 else False
    return x12