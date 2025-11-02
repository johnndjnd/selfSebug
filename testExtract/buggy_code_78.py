def hex_key(num):
    primes = ('2', '3', '5', '7', 'B', 'D')
    total = 1
    for i in range(0, len(num)):
        if num[i] in primes:
            total += 1
    return total


def hex_key(num):
    primes = ('2', '3', '5', '7', 'B', 'D')
    total = 1
    x2 = len(num)
    x3 = range(0, x2)
    for i in x3:
        x4 = num[i]
        x5 = x4 in primes
        if x5:
            total = total + 1
    return total