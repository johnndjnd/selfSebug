def correct_bracketing(brackets: str):
    depth = 0
    for b in brackets:
        if b == ">":
            depth += 1
        else:
            depth -= 1
        if depth < 0:
            return False
    return depth == 0


def correct_bracketing(brackets: str):
    depth = 0
    for b in brackets:
        x1 = b == ">"
        if x1:
            depth = depth + 1
        else:
            depth = depth - 1
        x2 = depth < 0
        if x2:
            return False
    x3 = depth == 0
    return x3