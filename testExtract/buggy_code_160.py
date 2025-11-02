def do_algebra(operator, operand):
    expression = str(operand[0])
    for oprt, oprn in zip(operator, operand[1:]):
        expression+=expression + oprt + str(oprn)
    return eval(expression)


def do_algebra(operator, operand):
    x1 = operand[0]
    expression = str(x1)
    x3 = operand[1:]
    x4 = zip(operator, x3)
    for oprt, oprn in x4:
        x5 = expression + oprt
        x6 = str(oprn)
        x7 = x5 + x6
        expression = expression + x7
    x8 = eval(expression)
    return x8