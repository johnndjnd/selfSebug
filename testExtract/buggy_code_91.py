def is_bored(S):
    import re
    sentences = re.split(r'[.?!]\s*', S)
    return sum(sentence[0:2] == ' I' for sentence in sentences)


def is_bored(S):
    import re
    sentences = re.split(r'[.?!]\s*', S)
    x2 = []
    for sentence in sentences:
        x3 = sentence[0:2]
        x4 = x3 == ' I'
        x2.append(x4)
    x6 = (x5 for x5 in x2)
    x7 = sum(x6)
    return x7