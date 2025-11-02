def get_max_triples(n):
    A = [i*i for i in range(1,n+1)]
    ans = []
    for i in range(n):
        for j in range(i+1,n):
            for k in range(j+1,n):
                if (A[i]+A[j]+A[k])%3 == 0:
                    ans += [(A[i],A[j],A[k])]
    return len(ans)


def get_max_triples(n):
    x1 = []
    x2 = n + 1
    x3 = range(1, x2)
    for i in x3:
        x4 = i * i
        x1.append(x4)
    A = x1
    ans = []
    x6 = range(n)
    for i in x6:
        x7 = i + 1
        x8 = range(x7, n)
        for j in x8:
            x9 = j + 1
            x10 = range(x9, n)
            for k in x10:
                x11 = A[i]
                x12 = A[j]
                x13 = x11 + x12
                x14 = A[k]
                x15 = x13 + x14
                x16 = x15 % 3
                x17 = x16 == 0
                if x17:
                    x18 = A[i]
                    x19 = A[j]
                    x20 = A[k]
                    x21 = (x18, x19, x20)
                    x22 = [x21]
                    ans = ans + x22
    x23 = len(ans)
    return x23