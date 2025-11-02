def valid_date(date):
    try:
        date = date.strip()
        day, month, year = date.split('-')
        day, month, year = int(day), int(month), int(year)
        if month < 1 or month > 12:
            return False
        if month in [1,3,5,7,8,10,12] and day < 1 or day > 31:
            return False
        if month in [4,6,9,11] and day < 1 or day > 30:
            return False
        if month == 2 and day < 1 or day > 29:
            return False
    except:
        return False

    return True


def valid_date(date):
    try:
        date = date.strip()
        x2 = date.split('-')
        day, month, year = x2
        x3 = int(day)
        x4 = int(month)
        x5 = int(year)
        x6 = (x3, x4, x5)
        day, month, year = x6
        x7 = month < 1
        x8 = month > 12
        x9 = x7 or x8
        if x9:
            return False
        x10 = [1, 3, 5, 7, 8, 10, 12]
        x11 = month in x10
        x12 = day < 1
        x13 = x11 and x12
        x14 = day > 31
        x15 = x13 or x14
        if x15:
            return False
        x16 = [4, 6, 9, 11]
        x17 = month in x16
        x18 = day < 1
        x19 = x17 and x18
        x20 = day > 30
        x21 = x19 or x20
        if x21:
            return False
        x22 = month == 2
        x23 = day < 1
        x24 = x22 and x23
        x25 = day > 29
        x26 = x24 or x25
        if x26:
            return False
    except:
        return False
    return True