def sort_array(array):
    return [] if len(array) == 0 else sorted(array, reverse= (array[0]+array[-1]) % 2 != 0) 


def sort_array(array):
    x1 = []
    x2 = len(array)
    x3 = x2 == 0
    x4 = array[0]
    x5 = -1
    x6 = array[x5]
    x7 = x4 + x6
    x8 = x7 % 2
    x9 = x8 != 0
    x10 = sorted(array, reverse=x9)
    x11 = x1 if x3 else x10
    return x11