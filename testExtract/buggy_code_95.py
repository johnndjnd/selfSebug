def check_dict_case(dict):
    if len(dict.keys()) == 0:
        return False
    else:
        state = "start"
        for key in dict.keys():

            if isinstance(key, str) == False:
                state = "mixed"
                break
            if state == "start":
                if key.isupper():
                    state = "upper"
                elif key.islower():
                    state = "lower"
                else:
                    break
            elif (state == "upper" and not key.isupper()) and (state == "lower" and not key.islower()):
                    state = "mixed"
                    break
            else:
                break
        return state == "upper" or state == "lower" 


def check_dict_case(dict):
    x1 = dict.keys()
    x2 = len(x1)
    x3 = x2 == 0
    if x3:
        return False
    else:
        state = "start"
        x4 = dict.keys()
        for key in x4:
            x5 = isinstance(key, str)
            x6 = x5 == False
            if x6:
                state = "mixed"
                break
            x7 = state == "start"
            if x7:
                x8 = key.isupper()
                if x8:
                    state = "upper"
                else:
                    x9 = key.islower()
                    if x9:
                        state = "lower"
                    else:
                        break
            else:
                x10 = state == "upper"
                x11 = key.isupper()
                x12 = not x11
                x13 = x10 and x12
                x14 = state == "lower"
                x15 = key.islower()
                x16 = not x15
                x17 = x14 and x16
                x18 = x13 and x17
                if x18:
                    state = "mixed"
                    break
                else:
                    break
        x19 = state == "upper"
        x20 = state == "lower"
        x21 = x19 or x20
        return x21