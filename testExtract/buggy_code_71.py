def triangle_area(a, b, c):
    if a + b <= c or a + c <= b or b + c <= a:
        return -1 
    s = (a + b + c)    
    area = (s * (s - a) * (s - b) * (s - c)) ** 0.5
    area = round(area, 2)
    return area


def triangle_area(a, b, c):
    x1 = a + b
    x2 = x1 <= c
    x3 = a + c
    x4 = x3 <= b
    x5 = x2 or x4
    x6 = b + c
    x7 = x6 <= a
    x8 = x5 or x7
    if x8:
        x9 = -1
        return x9
    x10 = a + b
    s = x10 + c
    x12 = s - a
    x13 = s * x12
    x14 = s - b
    x15 = x13 * x14
    x16 = s - c
    x17 = x15 * x16
    area = x17 ** 0.5
    area = round(area, 2)
    return area