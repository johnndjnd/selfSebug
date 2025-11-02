def digitSum(s):
    if s == "": return 0
    return sum(ord(char) if char.islower() else 0 for char in s)


def digitSum(s):
    x1 = s == ""
    if x1:
        return 0
    x2 = []
    for char in s:
        x3 = ord(char)
        x4 = char.islower()
        x5 = x3 if x4 else 0
        x2.append(x5)
    x7 = (x6 for x6 in x2)
    x8 = sum(x7)
    return x8