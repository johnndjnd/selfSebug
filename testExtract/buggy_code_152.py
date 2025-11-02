def compare(game,guess):
    return [abs(x-y)+abs(y-x) for x,y in zip(game,guess)]


def compare(game,guess):
    x1 = []
    x2 = zip(game, guess)
    for x,y in x2:
        x3 = x - y
        x4 = abs(x3)
        x5 = y - x
        x6 = abs(x5)
        x7 = x4 + x6
        x1.append(x7)
    return x1