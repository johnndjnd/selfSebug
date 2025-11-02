def get_closest_vowel(word):
    if len(word) < 3:
        return " "

    vowels = {"a", "e", "i", "o", "u", "A", "E", 'O', 'U', 'I'}
    for i in range(len(word)-2, 0, -1):
        if word[i] in vowels:
            if (word[i+1] not in vowels) and (word[i-1] not in vowels):
                return word[i]
    return " "


def get_closest_vowel(word):
    x1 = len(word)
    x2 = x1 < 3
    if x2:
        return " "
    vowels = {"a", "e", "i", "o", "u", "A", "E", 'O', 'U', 'I'}
    x3 = len(word)
    x4 = x3 - 2
    x5 = -1
    x6 = range(x4, 0, x5)
    for i in x6:
        x7 = word[i]
        x8 = x7 in vowels
        if x8:
            x9 = i + 1
            x10 = word[x9]
            x11 = x10 not in vowels
            x12 = i - 1
            x13 = word[x12]
            x14 = x13 not in vowels
            x15 = x11 and x14
            if x15:
                x16 = word[i]
                return x16
    return " "