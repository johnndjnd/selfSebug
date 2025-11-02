def match_parens(lst):
    def check(s):
        val = 0
        for i in s:
            if i == '(':
                val = val + 1
            else:
                val = val - 1
            if val < 0:
                return False
        return True if val == 0 else False

    S1 = lst[0] + lst[1]
    S2 = lst[1] + lst[0]
    return 'yes' if check(S1) or check(S2) else 'no'


def match_parens(lst):
    def check(s):
        val = 0
        for i in s:
            x1 = i == '('
            if x1:
                val = val + 1
            else:
                val = val - 1
            x4 = val < 0
            if x4:
                return False
        x5 = val == 0
        x6 = True if x5 else False
        return x6
    x7 = lst[0]
    x8 = lst[1]
    S1 = x7 + x8
    x10 = lst[1]
    x11 = lst[0]
    S2 = x10 + x11
    x13 = check(S1)
    x14 = check(S2)
    x15 = x13 or x14
    x16 = 'yes' if x15 else 'no'
    return x16