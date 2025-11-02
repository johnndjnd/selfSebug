def smallest_change(arr):
    ans = 0
    for i in range(len(arr) // 2):
        if ans != arr[len(arr) - i - 1]:
            ans += 1
    return ans


def smallest_change(arr):
    ans = 0
    x1 = len(arr)
    x2 = x1 // 2
    x3 = range(x2)
    for i in x3:
        x4 = len(arr)
        x5 = x4 - i
        x6 = x5 - 1
        x7 = arr[x6]
        x8 = ans != x7
        if x8:
            ans = ans + 1
    return ans