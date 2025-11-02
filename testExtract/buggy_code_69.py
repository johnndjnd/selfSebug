def search(lst):
    frq = [0] * (max(lst) + 1)
    for i in lst:
        frq[i] += 1;

    ans = 0
    for i in range(1, len(frq)):
        if frq[i] >= i:
            ans = i
    
    return ans


def search(lst):
    x1 = [0]
    x2 = max(lst)
    x3 = x2 + 1
    frq = x1 * x3
    for i in lst:
        x5 = frq[i]
        x5 = x5 + 1
    ans = 0
    x6 = len(frq)
    x7 = range(1, x6)
    for i in x7:
        x8 = frq[i]
        x9 = x8 >= i
        if x9:
            ans = i
    return ans