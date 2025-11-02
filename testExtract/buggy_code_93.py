def encode(message):
    vowels = "aeiou"
    vowels_replace = dict([(i, chr(ord(i) + 2)) for i in vowels])
    message = message.swapcase()
    return ''.join([vowels_replace[i] if i in vowels else i for i in message])


def encode(message):
    vowels = "aeiou"
    x1 = []
    for i in vowels:
        x2 = ord(i)
        x3 = x2 + 2
        x4 = chr(x3)
        x5 = (i, x4)
        x1.append(x5)
    vowels_replace = dict(x1)
    message = message.swapcase()
    x8 = []
    for i in message:
        x9 = vowels_replace[i]
        x10 = i in vowels
        x11 = x9 if x10 else i
        x8.append(x11)
    x12 = ''.join(x8)
    return x12