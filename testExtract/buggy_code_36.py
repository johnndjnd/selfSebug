def fizz_buzz(n: int):
    ns = []
    for i in range(n):
        if i % 11 == 0 and i % 13 == 0:
            ns.append(i)
    s = ''.join(list(map(str, ns)))
    ans = 0
    for c in s:
        ans += (c == '7')
    return ans


def fizz_buzz(n: int):
    ns = []
    x2 = range(n)
    for i in x2:
        x3 = i % 11
        x4 = x3 == 0
        x5 = i % 13
        x6 = x5 == 0
        x7 = x4 and x6
        if x7:
            ns.append(i)
    x8 = map(str, ns)
    x9 = list(x8)
    s = ''.join(x9)
    ans = 0
    for c in s:
        x11 = c == '7'
        ans = ans + x11
    return ans