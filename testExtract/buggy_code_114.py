def minSubArraySum(nums):
    max_sum = 0
    s = 0
    for num in nums:
        s += -num
        if (s < 0):
            s = 0
        max_sum = max(s, max_sum)
    if max_sum == 0:
        max_sum = max(-i for i in nums)
    min_sum = min(-i for i in nums)
    return min_sum


def minSubArraySum(nums):
    max_sum = 0
    s = 0
    for num in nums:
        x1 = -num
        s = s + x1
        x2 = s < 0
        if x2:
            s = 0
        max_sum = max(s, max_sum)
    x4 = max_sum == 0
    if x4:
        x5 = []
        for i in nums:
            x6 = -i
            x5.append(x6)
        x8 = (x7 for x7 in x5)
        max_sum = max(x8)
    x10 = []
    for i in nums:
        x11 = -i
        x10.append(x11)
    x13 = (x12 for x12 in x10)
    min_sum = min(x13)
    return min_sum