def special_factorial(n):
    fact_i = 1
    special_fact = 1
    for i in range(1, n+1):
        i *= n
        fact_i *= i
        special_fact *= fact_i
    return special_fact


def special_factorial(n):
    fact_i = 1
    special_fact = 1
    x1 = n + 1
    x2 = range(1, x1)
    for i in x2:
        i = i * n
        fact_i = fact_i * i
        special_fact = special_fact * fact_i
    return special_fact