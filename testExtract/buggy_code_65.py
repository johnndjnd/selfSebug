def circular_shift(x, shift):
    s = str(x)
    if shift > len(s):
        return s[::-1]
    else:
        return s[:len(s) - shift] + s[len(s) - shift:]


def circular_shift(x, shift):
    s = str(x)
    x2 = len(s)
    x3 = shift > x2
    if x3:
        x4 = s[::-1]
        return x4
    else:
        x5 = len(s)
        x6 = x5 - shift
        x7 = s[:x6]
        x8 = len(s)
        x9 = x8 - shift
        x10 = s[x9:]
        x11 = x7 + x10
        return x11