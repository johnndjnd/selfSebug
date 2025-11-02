from typing import List


def all_prefixes(string: str) -> List[str]:
    result = []

    for i in range(len(string)-1):
        result.append(string[:i+1])
    return result


from typing import List   # 未分解语句
def all_prefixes(string: str):
    result = []
    x2 = len(string)
    x3 = x2 - 1
    x4 = range(x3)
    for i in x4:
        x5 = i + 1
        x6 = string[:x5]
        result.append(x6)
    return result