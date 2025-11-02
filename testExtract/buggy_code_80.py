def is_happy(s):
    if len(s) < 3:
      return False

    for i in range(len(s) - 2):
      
      if s[i] == s[i+1] and s[i+1] == s[i+2] and s[i] == s[i+2]:
        return False
    return True


def is_happy(s):
    x1 = len(s)
    x2 = x1 < 3
    if x2:
        return False
    x3 = len(s)
    x4 = x3 - 2
    x5 = range(x4)
    for i in x5:
        x6 = s[i]
        x7 = i + 1
        x8 = s[x7]
        x9 = x6 == x8
        x10 = i + 1
        x11 = s[x10]
        x12 = i + 2
        x13 = s[x12]
        x14 = x11 == x13
        x15 = x9 and x14
        x16 = s[i]
        x17 = i + 2
        x18 = s[x17]
        x19 = x16 == x18
        x20 = x15 and x19
        if x20:
            return False
    return True