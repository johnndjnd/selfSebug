def is_nested(string):
    opening_bracket_index = []
    closing_bracket_index = []
    for i in range(len(string)):
        if string[i] == '(':
            opening_bracket_index.append(i)
        else:
            closing_bracket_index.append(i)
    closing_bracket_index.reverse()
    cnt = 0
    i = 0
    l = len(closing_bracket_index)
    for idx in opening_bracket_index:
        if i < l and idx < closing_bracket_index[i]:
            cnt += 1
            i += 1
    return cnt >= 2

    


def is_nested(string):
    opening_bracket_index = []
    closing_bracket_index = []
    x3 = len(string)
    x4 = range(x3)
    for i in x4:
        x5 = string[i]
        x6 = x5 == '('
        if x6:
            opening_bracket_index.append(i)
        else:
            closing_bracket_index.append(i)
    closing_bracket_index.reverse()
    cnt = 0
    i = 0
    l = len(closing_bracket_index)
    for idx in opening_bracket_index:
        x8 = i < l
        x9 = closing_bracket_index[i]
        x10 = idx < x9
        x11 = x8 and x10
        if x11:
            cnt = cnt + 1
            i = i + 1
    x12 = cnt >= 2
    return x12