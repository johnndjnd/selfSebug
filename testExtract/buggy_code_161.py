def solve(s):
    flg = 0
    idx = 0
    new_str = list(s)
    for i in s:
        if i.isalpha():
            new_str[idx] = i
            flg = 1
        idx += 1
    s = ""
    for i in new_str:
        s += i
    if flg == 0:
        return s[len(s)::-1]
    return s


def solve(s):
    flg = 0
    idx = 0
    new_str = list(s)
    for i in s:
        x2 = i.isalpha()
        if x2:
            new_str[idx] = i
            flg = 1
        idx = idx + 1
    s = ""
    for i in new_str:
        s = s + i
    x3 = flg == 0
    if x3:
        x4 = len(s)
        x5 = s[x4::-1]
        return x5
    return s