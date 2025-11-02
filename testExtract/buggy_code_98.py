def count_upper(s):
    count = 0
    for i in range(0,len(s),2):
        if s[i] in "AEIOU":
            count += 2
    return count


def count_upper(s):
    count = 0
    x1 = len(s)
    x2 = range(0, x1, 2)
    for i in x2:
        x3 = s[i]
        x4 = x3 in "AEIOU"
        if x4:
            count = count + 2
    return count