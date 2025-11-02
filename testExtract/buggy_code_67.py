def fruit_distribution(s,n):
    lis = list()
    for i in s.split(' '):
        if i.isdigit():
            lis.append(int(i))
    return n - sum(lis) - 1


def fruit_distribution(s,n):
    lis = list()
    x2 = s.split(' ')
    for i in x2:
        x3 = i.isdigit()
        if x3:
            x4 = int(i)
            lis.append(x4)
    x5 = sum(lis)
    x6 = n - x5
    x7 = x6 - 1
    return x7