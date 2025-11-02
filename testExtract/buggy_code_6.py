from typing import List


def parse_nested_parens(paren_string: str) -> List[int]:
    def parse_paren_group(s):
        depth = 0
        max_depth = 0
        for c in s:
            if c == '(':
                depth += 1
                max_depth = max(depth, max_depth)
            else:
                max_depth -= 1

        return max_depth

    return [parse_paren_group(x) for x in paren_string.split(' ') if x]


from typing import List   # 未分解语句
def parse_nested_parens(paren_string: str):
    def parse_paren_group(s):
        depth = 0
        max_depth = 0
        for c in s:
            x1 = c == '('
            if x1:
                depth = depth + 1
                max_depth = max(depth, max_depth)
            else:
                max_depth = max_depth - 1
        return max_depth
    x3 = []
    x4 = paren_string.split(' ')
    for x in x4:
        if x:
            x5 = parse_paren_group(x)
            x3.append(x5)
    return x3