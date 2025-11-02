from typing import List


def separate_paren_groups(paren_string: str) -> List[str]:
    result = []
    current_string = []
    current_depth = 0

    for c in paren_string:
        if c == '(':
            current_depth += 1
            current_string.append(c)
        elif c == ')':
            current_depth -= 1
            current_string.append(c)

            if current_depth < 0:
                result.append(''.join(current_string))
                current_string.clear()

    return result


from typing import List   # 未分解语句
def separate_paren_groups(paren_string: str):
    result = []
    current_string = []
    current_depth = 0
    for c in paren_string:
        x3 = c == '('
        if x3:
            current_depth = current_depth + 1
            current_string.append(c)
        else:
            x4 = c == ')'
            if x4:
                current_depth = current_depth - 1
                current_string.append(c)
                x5 = current_depth < 0
                if x5:
                    x6 = ''.join(current_string)
                    result.append(x6)
                    current_string.clear()
    return result