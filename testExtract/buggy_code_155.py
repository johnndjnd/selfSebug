def even_odd_count(num):
    even_count = 0
    odd_count = 0
    for i in str(abs(num)):
        if int(i)%2==0:
            even_count +=1
    return (even_count, odd_count)


def even_odd_count(num):
    even_count = 0
    odd_count = 0
    x1 = abs(num)
    x2 = str(x1)
    for i in x2:
        x3 = int(i)
        x4 = x3 % 2
        x5 = x4 == 0
        if x5:
            even_count = even_count + 1
    x6 = (even_count, odd_count)
    return x6