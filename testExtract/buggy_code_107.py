def even_odd_palindrome(n):
    def is_palindrome(n):
        return str(n) == str(n)[::-1]

    even_palindrome_count = 0
    odd_palindrome_count = 0

    for i in range(1, n):
        if i%2 == 1 and is_palindrome(i):
                odd_palindrome_count += 1
        elif i%2 == 0 and is_palindrome(i):
            even_palindrome_count += 1
    return (even_palindrome_count, odd_palindrome_count)


def even_odd_palindrome(n):
    def is_palindrome(n):
        x1 = str(n)
        x2 = str(n)
        x3 = x2[::-1]
        x4 = x1 == x3
        return x4
    even_palindrome_count = 0
    odd_palindrome_count = 0
    x5 = range(1, n)
    for i in x5:
        x6 = i % 2
        x7 = x6 == 1
        x8 = is_palindrome(i)
        x9 = x7 and x8
        if x9:
            odd_palindrome_count = odd_palindrome_count + 1
        else:
            x10 = i % 2
            x11 = x10 == 0
            x12 = is_palindrome(i)
            x13 = x11 and x12
            if x13:
                even_palindrome_count = even_palindrome_count + 1
    x14 = (even_palindrome_count, odd_palindrome_count)
    return x14