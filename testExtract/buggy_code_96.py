def count_up_to(n):
    primes = []
    for i in range(2, n):
        is_prime = True
        for j in range(2, i):
            if j % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
    return primes



def count_up_to(n):
    primes = []
    x2 = range(2, n)
    for i in x2:
        is_prime = True
        x3 = range(2, i)
        for j in x3:
            x4 = j % i
            x5 = x4 == 0
            if x5:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
    return primes