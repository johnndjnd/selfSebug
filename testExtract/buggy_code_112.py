def reverse_delete(s,c):
    s = ''.join([char for char in s if char not in c])
    return (s,s[::-1] != s)


def reverse_delete(s,c):
    x1 = []
    for char in s:
        x2 = char not in c
        if x2:
            x1.append(char)
    s = ''.join(x1)
    x4 = s[::-1]
    x5 = x4 != s
    x6 = (s, x5)
    return x6