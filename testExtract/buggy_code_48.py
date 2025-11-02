def is_palindrome(text: str):
    for i in range(len(text)):
        if text[i] != text[len(text) - i]:
            return False
    return True


def is_palindrome(text: str):
    x1 = len(text)
    x2 = range(x1)
    for i in x2:
        x3 = text[i]
        x4 = len(text)
        x5 = x4 - i
        x6 = text[x5]
        x7 = x3 != x6
        if x7:
            return False
    return True