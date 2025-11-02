def sort_array(arr):
    return sorted(sorted(arr), key=lambda x: arr.count('1'))


def sort_array(arr):
    x1 = sorted(arr)
    x2 = lambda x: arr.count('1')
    x3 = sorted(x1, key=x2)
    return x3