def encode_cyclic(s: str):
    """
    returns encoded string by cycling groups of three characters.
    """
    # split string to groups. Each of length 3.
    groups = [s[(3 * i):min((3 * i + 3), len(s))] for i in range((len(s) + 2) // 3)]
    # cycle elements in each group. Unless group has fewer elements than 3.
    groups = [(group[1:] + group[0]) if len(group) == 3 else group for group in groups]
    return "".join(groups)


def decode_cyclic(s: str):
    return encode_cyclic(s)


def encode_cyclic(s: str):
    x1 = []
    x2 = len(s)
    x3 = x2 + 2
    x4 = x3 // 3
    x5 = range(x4)
    for i in x5:
        x6 = 3 * i
        x7 = 3 * i
        x8 = x7 + 3
        x9 = len(s)
        x10 = min(x8, x9)
        x11 = s[x6:x10]
        x1.append(x11)
    groups = x1
    x12 = []
    for group in groups:
        x13 = group[1:]
        x14 = group[0]
        x15 = x13 + x14
        x16 = len(group)
        x17 = x16 == 3
        x18 = x15 if x17 else group
        x12.append(x18)
    groups = x12
    x19 = "".join(groups)
    return x19
def decode_cyclic(s: str):
    x20 = encode_cyclic(s)
    return x20