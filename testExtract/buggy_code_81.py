def numerical_letter_grade(grades):

   
    letter_grade = []
    for gpa in grades:
        if gpa == 4.0:
            letter_grade.append("A+")
        elif gpa > 3.7:
            letter_grade.append("A")
        elif gpa > 3.3:
            letter_grade.append("A-")
        elif gpa > 3.0:
            letter_grade.append("B+")
        elif gpa > 2.7:
            letter_grade.append("B")
        elif gpa > 2.3:
            letter_grade.append("B-")
        elif gpa > 2.0:
            letter_grade.append("C+")
        elif gpa > 1.7:
            letter_grade.append("C")
        elif gpa > 1.3:
            letter_grade.append("C-")
        elif gpa > 1.0:
            letter_grade.append("D+")
        elif gpa > 0.7:
            letter_grade.append("D")
        elif gpa > 0.0:
            letter_grade.append("D-")
        else:
            letter_grade.append("E+")
    return letter_grade


def numerical_letter_grade(grades):
    letter_grade = []
    for gpa in grades:
        x2 = gpa == 4.0
        if x2:
            letter_grade.append("A+")
        else:
            x3 = gpa > 3.7
            if x3:
                letter_grade.append("A")
            else:
                x4 = gpa > 3.3
                if x4:
                    letter_grade.append("A-")
                else:
                    x5 = gpa > 3.0
                    if x5:
                        letter_grade.append("B+")
                    else:
                        x6 = gpa > 2.7
                        if x6:
                            letter_grade.append("B")
                        else:
                            x7 = gpa > 2.3
                            if x7:
                                letter_grade.append("B-")
                            else:
                                x8 = gpa > 2.0
                                if x8:
                                    letter_grade.append("C+")
                                else:
                                    x9 = gpa > 1.7
                                    if x9:
                                        letter_grade.append("C")
                                    else:
                                        x10 = gpa > 1.3
                                        if x10:
                                            letter_grade.append("C-")
                                        else:
                                            x11 = gpa > 1.0
                                            if x11:
                                                letter_grade.append("D+")
                                            else:
                                                x12 = gpa > 0.7
                                                if x12:
                                                    letter_grade.append("D")
                                                else:
                                                    x13 = gpa > 0.0
                                                    if x13:
                                                        letter_grade.append("D-")
                                                    else:
                                                        letter_grade.append("E+")
    return letter_grade