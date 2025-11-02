def decimal_to_binary(decimal):
    return "db" + bin(decimal)[2:] + "d"


def decimal_to_binary(decimal):
    x1 = bin(decimal)
    x2 = x1[2:]
    x3 = "db" + x2
    x4 = x3 + "d"
    return x4