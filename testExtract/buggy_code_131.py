def digits(n):
    product = 1
    odd_count = 0
    for digit in str(n):
        int_digit = int(digit)
        if int_digit%2 == 1:
            product*= product*int_digit
            odd_count+=1
    if odd_count ==0:
        return 0
    else:
        return product


def digits(n):
    product = 1
    odd_count = 0
    x1 = str(n)
    for digit in x1:
        int_digit = int(digit)
        x3 = int_digit % 2
        x4 = x3 == 1
        if x4:
            x5 = product * int_digit
            product = product * x5
            odd_count = odd_count + 1
    x6 = odd_count == 0
    if x6:
        return 0
    else:
        return product