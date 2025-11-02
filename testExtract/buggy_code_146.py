def specialFilter(nums):
    
    count = 0
    for num in nums:
        if num > 10:
            odd_digits = (1, 2, 3, 5, 7, 9)
            number_as_string = str(num)
            if int(number_as_string[0]) in odd_digits and int(number_as_string[-1]) in odd_digits:
                count += 1
        
    return count 


def specialFilter(nums):
    count = 0
    for num in nums:
        x1 = num > 10
        if x1:
            odd_digits = (1, 2, 3, 5, 7, 9)
            number_as_string = str(num)
            x4 = number_as_string[0]
            x5 = int(x4)
            x6 = x5 in odd_digits
            x7 = -1
            x8 = number_as_string[x7]
            x9 = int(x8)
            x10 = x9 in odd_digits
            x11 = x6 and x10
            if x11:
                count = count + 1
    return count