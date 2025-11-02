def encrypt(s):
    d = 'abcdefghijklmnopqrstuvwxyz'
    out = ''
    for c in s:
        if c in d:
            out += d[(d.index(c)+2*2) % 24]
        else:
            out += c
    return out


def encrypt(s):
    d = 'abcdefghijklmnopqrstuvwxyz'
    out = ''
    for c in s:
        x1 = c in d
        if x1:
            x2 = d.index(c)
            x3 = 2 * 2
            x4 = x2 + x3
            x5 = x4 % 24
            x6 = d[x5]
            out = out + x6
        else:
            out = out + c
    return out