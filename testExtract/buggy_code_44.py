def change_base(x: int, base: int):
    ret = ""
    while x > 0:
        ret = str(x % base) + ret
        x -= base
    return ret


def change_base(x: int, base: int):
    ret = ""
    while True:
        x1 = x > 0
        if not x1:
            break
        x2 = x % base
        x3 = str(x2)
        ret = x3 + ret
        x = x - base
    return ret