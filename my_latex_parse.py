from re import sub as subsitute
from rational_processes import ComplexRationalObject, RationalObject

a = ['\\frac{(n+2)}{10n^2+20n}', '\\frac{(30n-24)}{54n^2}', '\\frac{81x}{18x^2+90}', '\\frac{(x+40)}{2x^2+99x+760}', 
     '\\frac{(21n-49)}{7-3n}\\cdot\\frac{(5n^2+30n+25)}{35n+35}', '\\frac{(8p^3-32p^2)}{5p^2+28p-49}\\cdot\\frac{(5p-7)}{8p^3-64p^2}', '\\frac{\\frac{(5x-40)}{25x+15}}{\\frac{6x}{20x+12}}', 
     '\\frac{3}{x-1}+\\frac{6x}{2x+3}', '\\frac{7x}{x-5}-\\frac{4}{5-x}', '\\frac{(x^2-12x+1)}{x+5}+\\frac{(x^2-9)}{x-4}', '\\frac{4}{7x+2}+\\frac{8}{6x-5}+\\frac{(-3)}{14x-9}+\\frac{17}{x-1}-\\frac{1}{x}', 
     '\\frac{2}{5}+\\frac{4}{10x+5}=\\frac{7}{2x+1}', '\\frac{10}{x^2-2x}+\\frac{4}{x}=\\frac{5}{x-2}', '\\frac{1}{6k^2}=\\frac{1}{3k^2}-\\frac{1}{k}', '\\frac{1}{v}+\\frac{(3v+12)}{v^2-5v}=\\frac{(7v-56)}{v^2-5v}',
      '\\frac{1}{m^2-m}+\\frac{1}{m}=\\frac{5}{m^2-m}', '\\frac{(p+5)}{p^2+p}=\\frac{1}{p^2+p}-\\frac{(p-6)}{p+1}', '\\frac{(x^2+16x-4)}{x^3-4x}', '\\frac{(x^3-4x^2-4x-9)}{x^2-5x-6}', '\\frac{(x+7)}{x^2-x-6}', 
      '\\frac{(-5x-18)}{2x^2+11x-21}', '-\\frac{-2x+3}{x^2+x}', '\\frac{10402x^4-12313x^3+1145x^2+1441x+90}{588x^5-1288x^4+767x^3+23x^2-90x}+23']

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
