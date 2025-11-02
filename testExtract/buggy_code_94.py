def skjkasdkd(lst):
    def isPrime(n):
        for i in range(2,int(n**0.5)+1):
            if n%i==0:
                return True

        return False
    maxx = 0
    i = 0
    while i < len(lst):
        if(lst[i] > maxx and isPrime(lst[i])):
            maxx = lst[i]
        i+=1
    result = sum(int(digit) for digit in str(maxx))
    return result



def skjkasdkd(lst):
    def isPrime(n):
        x1 = n ** 0.5
        x2 = int(x1)
        x3 = x2 + 1
        x4 = range(2, x3)
        for i in x4:
            x5 = n % i
            x6 = x5 == 0
            if x6:
                return True
        return False
    maxx = 0
    i = 0
    while True:
        x7 = len(lst)
        x8 = i < x7
        if not x8:
            break
        x9 = lst[i]
        x10 = x9 > maxx
        x11 = lst[i]
        x12 = isPrime(x11)
        x13 = x10 and x12
        if x13:
            maxx = lst[i]
        i = i + 1
    x15 = []
    x16 = str(maxx)
    for digit in x16:
        x17 = int(digit)
        x15.append(x17)
    x19 = (x18 for x18 in x15)
    result = sum(x19)
    return result