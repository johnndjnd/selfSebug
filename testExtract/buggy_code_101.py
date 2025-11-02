def words_string(s):
    if not s:
        return []

    s_list = []

    for letter in s:
        if letter == ',':
            s_list.append(',')
        else:
            s_list.append(letter)

    s_list = "".join(s_list)
    return s_list.split()


def words_string(s):
    x1 = not s
    if x1:
        x2 = []
        return x2
    s_list = []
    for letter in s:
        x4 = letter == ','
        if x4:
            s_list.append(',')
        else:
            s_list.append(letter)
    s_list = "".join(s_list)
    x6 = s_list.split()
    return x6