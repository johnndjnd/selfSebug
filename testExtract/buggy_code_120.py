def maximum(arr, k):
    if k == 0:
        return []
    arr.sort()
    ans = arr[-k:]
    return ans.sort(reverse=True)


def maximum(arr, k):
    x1 = k == 0
    if x1:
        x2 = []
        return x2
    arr.sort()
    x3 = -k
    ans = arr[x3:]
    x5 = ans.sort(reverse=True)
    return x5