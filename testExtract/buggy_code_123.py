def get_odd_collatz(n):
    if n%2==0:
        odd_collatz = [] 
    else:
        odd_collatz = [n]
    while n > 1:
        if n % 2 == 0:
            n = n/2
        else:
            n = n*2 + 1
            
        if n%2 == 1:
            odd_collatz.append(int(n))

    return sorted(odd_collatz)


def get_odd_collatz(n):
    x1 = n % 2
    x2 = x1 == 0
    if x2:
        odd_collatz = []
    else:
        odd_collatz = [n]
    while True:
        x5 = n > 1
        if not x5:
            break
        x6 = n % 2
        x7 = x6 == 0
        if x7:
            n = n / 2
        else:
            x9 = n * 2
            n = x9 + 1
        x11 = n % 2
        x12 = x11 == 1
        if x12:
            x13 = int(n)
            odd_collatz.append(x13)
    x14 = sorted(odd_collatz)
    return x14