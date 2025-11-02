def words_in_sentence(sentence):
    new_lst = []
    for word in sentence.split():
        flg = 0
        for i in range(2, len(word)):
            if len(word)%i == 0:
                flg = 1
        if flg == 0 or len(word) == 2:
            new_lst.append(word)
    return " ".join(new_lst)


def words_in_sentence(sentence):
    new_lst = []
    x2 = sentence.split()
    for word in x2:
        flg = 0
        x3 = len(word)
        x4 = range(2, x3)
        for i in x4:
            x5 = len(word)
            x6 = x5 % i
            x7 = x6 == 0
            if x7:
                flg = 1
        x8 = flg == 0
        x9 = len(word)
        x10 = x9 == 2
        x11 = x8 or x10
        if x11:
            new_lst.append(word)
    x12 = " ".join(new_lst)
    return x12