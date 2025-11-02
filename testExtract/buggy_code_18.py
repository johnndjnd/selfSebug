def how_many_times(string: str, substring: str) -> int:
    times = 0

    for i in range(len(string) - len(substring)):
        if string[i:i+len(substring)] == substring:
            times += 1

    return times


def how_many_times(string: str, substring: str):
    times = 0
    x1 = len(string)
    x2 = len(substring)
    x3 = x1 - x2
    x4 = range(x3)
    for i in x4:
        x5 = len(substring)
        x6 = i + x5
        x7 = string[i:x6]
        x8 = x7 == substring
        if x8:
            times = times + 1
    return times