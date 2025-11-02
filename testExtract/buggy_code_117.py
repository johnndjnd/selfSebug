def select_words(s, n):
    result = []
    for word in s.split():
        n_consonants = 0
        for i in range(0, len(word)):
            if word[i].lower() in ["a","e","i","o","u"]:
                n_consonants += 1 
        if n_consonants == n:
            result.append(word)
    return result



def select_words(s, n):
    result = []
    x2 = s.split()
    for word in x2:
        n_consonants = 0
        x3 = len(word)
        x4 = range(0, x3)
        for i in x4:
            x5 = word[i]
            x6 = x5.lower()
            x7 = ["a", "e", "i", "o", "u"]
            x8 = x6 in x7
            if x8:
                n_consonants = n_consonants + 1
        x9 = n_consonants == n
        if x9:
            result.append(word)
    return result