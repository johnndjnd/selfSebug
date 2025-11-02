def compare_one(a, b):
    temp_a, temp_b = a, b
    if isinstance(temp_a, str): temp_a = temp_a.replace(',','.').replace('.',',')
    if isinstance(temp_b, str): temp_b = temp_b.replace(',','.')
    if float(temp_a) == float(temp_b): return None
    return a if float(temp_a) > float(temp_b) else b 


def compare_one(a, b):
    x1 = (a, b)
    temp_a, temp_b = x1
    x2 = isinstance(temp_a, str)
    if x2:
        x3 = temp_a.replace(',', '.')
        temp_a = x3.replace('.', ',')
    x5 = isinstance(temp_b, str)
    if x5:
        temp_b = temp_b.replace(',', '.')
    x7 = float(temp_a)
    x8 = float(temp_b)
    x9 = x7 == x8
    if x9:
        return None
    x10 = float(temp_a)
    x11 = float(temp_b)
    x12 = x10 > x11
    x13 = a if x12 else b
    return x13