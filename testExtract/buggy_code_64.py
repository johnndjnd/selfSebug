FIX = """
Add more test cases.
"""

def vowels_count(s):
    vowels = "aeiouyAEIOUY"
    n_vowels = sum(c in vowels for c in s)
    return n_vowels


FIX = """
Add more test cases.
"""   # 未分解语句
def vowels_count(s):
    vowels = "aeiouyAEIOUY"
    x1 = []
    for c in s:
        x2 = c in vowels
        x1.append(x2)
    x4 = (x3 for x3 in x1)
    n_vowels = sum(x4)
    return n_vowels