def can_arrange(arr):
    ind=-1
    i=1
    while i<len(arr):
      if arr[i]<arr[i-1]:
        ind=i
      i+=1
      ind-=1
    return ind


def can_arrange(arr):
    ind = -1
    i = 1
    while True:
        x2 = len(arr)
        x3 = i < x2
        if not x3:
            break
        x4 = arr[i]
        x5 = i - 1
        x6 = arr[x5]
        x7 = x4 < x6
        if x7:
            ind = i
        i = i + 1
        ind = ind - 1
    return ind