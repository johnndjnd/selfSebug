def is_simple_power(x, n):
    if (n == 1): 
        return (x == 1) 
    power = 1
    while (n < x): 
        power = power * n 
    return (power == x) 


def is_simple_power(x, n):
    x1 = n == 1
    if x1:
        x2 = x == 1
        return x2
    power = 1
    while True:
        x3 = n < x
        if not x3:
            break
        power = power * n
    x5 = power == x
    return x5