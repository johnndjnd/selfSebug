def move_one_ball(arr):
    if len(arr)==0:
      return True
    sorted_array=sorted(arr)
    my_arr=[]
    
    min_value=min(arr)
    min_index=sorted_array.index(min_value)
    my_arr=arr[min_index:]+arr[0:min_index]
    for i in range(len(arr)):
      if my_arr[i]!=sorted_array[i]:
        return False
    return True


def move_one_ball(arr):
    x1 = len(arr)
    x2 = x1 == 0
    if x2:
        return True
    sorted_array = sorted(arr)
    my_arr = []
    min_value = min(arr)
    min_index = sorted_array.index(min_value)
    x7 = arr[min_index:]
    x8 = arr[0:min_index]
    my_arr = x7 + x8
    x10 = len(arr)
    x11 = range(x10)
    for i in x11:
        x12 = my_arr[i]
        x13 = sorted_array[i]
        x14 = x12 != x13
        if x14:
            return False
    return True