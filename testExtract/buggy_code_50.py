def encode_shift(s: str):
    """
    returns encoded string by shifting every character by 5 in the alphabet.
    """
    return "".join([chr(((ord(ch) + 5 - ord("a")) % 26) + ord("a")) for ch in s])


def decode_shift(s: str):
    return "".join([chr(((ord(ch) - 5 - ord("a")) % 26) + ord(ch)) for ch in s])


def encode_shift(s: str):
    x1 = []
    for ch in s:
        x2 = ord(ch)
        x3 = x2 + 5
        x4 = ord("a")
        x5 = x3 - x4
        x6 = x5 % 26
        x7 = ord("a")
        x8 = x6 + x7
        x9 = chr(x8)
        x1.append(x9)
    x10 = "".join(x1)
    return x10
def decode_shift(s: str):
    x11 = []
    for ch in s:
        x12 = ord(ch)
        x13 = x12 - 5
        x14 = ord("a")
        x15 = x13 - x14
        x16 = x15 % 26
        x17 = ord(ch)
        x18 = x16 + x17
        x19 = chr(x18)
        x11.append(x19)
    x20 = "".join(x11)
    return x20