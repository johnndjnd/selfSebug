def intersection(interval1, interval2):
    def is_prime(num):
        if num == 1 or num == 0:
            return False
        if num == 2:
            return True
        for i in range(2, num):
            if num%i == 0:
                return False
        return True

    l = max(interval1[0], interval2[0])
    r = min(interval1[1], interval2[1])
    length = r - l
    if length > 0:
        return "YES"
    return "NO"


def intersection(interval1, interval2):
    def is_prime(num):
        x1 = num == 1
        x2 = num == 0
        x3 = x1 or x2
        if x3:
            return False
        x4 = num == 2
        if x4:
            return True
        x5 = range(2, num)
        for i in x5:
            x6 = num % i
            x7 = x6 == 0
            if x7:
                return False
        return True
    x8 = interval1[0]
    x9 = interval2[0]
    l = max(x8, x9)
    x11 = interval1[1]
    x12 = interval2[1]
    r = min(x11, x12)
    length = r - l
    x15 = length > 0
    if x15:
        return "YES"
    return "NO"