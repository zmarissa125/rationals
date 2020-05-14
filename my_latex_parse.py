"""
This file parses the latex input from the web app


This is a mess of logic and loops. 
Sorry.
"""

from re import sub as subsitute
from base_rationals import ComplexRationalObject, RationalObject


def first_proccess(latex_str):
    latex_str = subsitute(r"\\frac|\\left|\\right", "", latex_str)
    latex_str = subsitute(r"\\cdot", "*", latex_str)
    latex_str = subsitute("\^", "**", latex_str)
    latex_str = subsitute("([0-9]+)([a-z]+)", r"\g<1>*\g<2>", latex_str)
    latex_str = subsitute("([a-z]+)(\()", r"\g<1>*\g<2>", latex_str)
    latex_str = subsitute("([0-9]+)(\()", r"\g<1>*\g<2>", latex_str)
    latex_str = subsitute("(\))(\()", r"\g<1>*\g<2>", latex_str)

    counter = 0
    output = []
    temp_frac = []
    outside =[]
    for char in latex_str:

        if char == "{":
            counter += 1
            if outside:
                output.append("".join(outside))
            outside = []
        elif char == "}":
            counter -= 1
        
        if counter > 0:
            temp_frac.append(char)
        
        if counter == 0:
            if temp_frac:
                output.append("".join(temp_frac))
                temp_frac = []
            elif check_if_int(char):
                outside.append(char)
            else:
                if outside:
                    output.append("".join(outside))
                    outside = []
                output.append(char)
    if outside:
        output.append("".join(outside))
    return output

def create_expression_data(list_of_data, complex_frac):
    expression_data =[]
    for index, part in enumerate(list_of_data):
        before = list_of_data[index-1]
        if "{" in part and "{" in before and index != 0:
            if r"{{" not in part:
                before, part = subsitute("{|}", "", before), subsitute("{|}", "", part)
                rational = [RationalObject(before, part)]
            else:
                n, d = first_proccess(before[1:]), first_proccess(part[1:])
                n_expr_data, d_expr_data = create_expression_data(n, complex_frac), create_expression_data(d, complex_frac)
                
                if len(n_expr_data) == 1 and len(d_expr_data) == 1 and complex_frac == False:
                    rational = [RationalObject(n_expr_data[0].numerator, n_expr_data[0].denomenator), "/", RationalObject(d_expr_data[0].numerator, d_expr_data[0].denomenator)]
                else:
                    rational = [ComplexRationalObject(n_expr_data, d_expr_data)]
            
            expression_data += rational
        
        elif check_if_int(part):
            expression_data.append(RationalObject(part, 1))
        
        elif "{" not in part:
            expression_data.append(part)
    return expression_data

def check_if_int(pos_string):
    try:
        int(pos_string)
        return True
    except:
        return False


def latex_to_data(latex_str, complex_frac = False):
    unprocessed_data = first_proccess(latex_str)
    expression_data = create_expression_data(unprocessed_data, complex_frac)
    return expression_data 
