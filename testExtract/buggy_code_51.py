def remove_vowels(text):
    return "".join([s for s in text if s.lower() not in ["a", "e", "i", "o", "u", "w", "y"]])


def remove_vowels(text):
    x1 = []
    for s in text:
        x2 = s.lower()
        x3 = ["a", "e", "i", "o", "u", "w", "y"]
        x4 = x2 not in x3
        if x4:
            x1.append(s)
    x5 = "".join(x1)
    return x5