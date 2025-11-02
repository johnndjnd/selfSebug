def histogram(test):
    dict1={}
    list1=test.split(" ")
    t=1

    for i in list1:
        if(list1.count(i)>t) and i!='':
            t=list1.count(i)
    if t>0:
        for i in list1:
            if(list1.count(i)==t):
                
                dict1[i]=t
    return dict1


def histogram(test):
    dict1 = {}
    list1 = test.split(" ")
    t = 1
    for i in list1:
        x2 = list1.count(i)
        x3 = x2 > t
        x4 = i != ''
        x5 = x3 and x4
        if x5:
            t = list1.count(i)
    x7 = t > 0
    if x7:
        for i in list1:
            x8 = list1.count(i)
            x9 = x8 == t
            if x9:
                dict1[i] = t
    return dict1