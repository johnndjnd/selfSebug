def solution(lst):
    return sum([x for idx, x in enumerate(lst) if idx%2==1 and x%2==1])


def solution(lst):
    x1 = []
    x2 = enumerate(lst)
    for idx, x in x2:
        x3 = idx % 2
        x4 = x3 == 1
        x5 = x % 2
        x6 = x5 == 1
        x7 = x4 and x6
        if x7:
            x1.append(x)
    x8 = sum(x1)
    return x8