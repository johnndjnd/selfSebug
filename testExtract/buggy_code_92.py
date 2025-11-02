def any_int(x, y, z):
    
    if isinstance(x,int) and isinstance(y,int) and isinstance(z,int):
        if (x+y==z) or (y+z==x):
            return True
        return False
    return False


def any_int(x, y, z):
    x1 = isinstance(x, int)
    x2 = isinstance(y, int)
    x3 = x1 and x2
    x4 = isinstance(z, int)
    x5 = x3 and x4
    if x5:
        x6 = x + y
        x7 = x6 == z
        x8 = y + z
        x9 = x8 == x
        x10 = x7 or x9
        if x10:
            return True
        return False
    return False