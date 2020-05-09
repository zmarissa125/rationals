from collections import Counter
from re import findall, split
from re import sub as subsitute

from sympy import cancel, expand, factor, latex, pretty_print, simplify, sympify, factor_list, solve, evalf, degree, div, Eq, Matrix, linsolve
from sympy.parsing.latex import parse_latex

from rational_processes import *



class Expression(object):
    """
    Takes in rational expression string, processes it, and outputs an answer and instructions
    Can only take in one operation at a time (excluding negative sign)
    
    Class and instance variables:
    expression_data is the broken down expression, a list of operators and RationalObjects 
             (all variables that end in expression_data are in this form)

    
    Class methods:
    Two constructors - standard __init__ and from_latex()
    process_expression() takes expression_data and directs it to functions based on operator
    """
    
    def __init__(self, input_str):
        """
        Creates Expression instance and sets expression_data variable, prints out input expression
         
        input_str must be in this form: ((numerator1)/(denomenator1)) operator ((numerator2)/(denomenator2)), 
                multiplication must be denoted with *, and must appear between all items in a term
                exponents denoted with **
        """

        self.expression_data = self.input_to_expr(input_str)

    def input_to_expr(self, input_str):
        expression_data = []
        broken_down = findall("\s?(-|\+|\*|/)?\s?\(?\(?\(?\(?(\(.+?\)|[0-9]*|.+?)/([a-z]*\*\*[0-9]*|\(.+?\)|[a-z]+?|[0-9]*|.*?|)\)?\)?\)?", input_str) 
        
        for rational in broken_down:
            if rational[0]:
                expression_data.append(rational[0])
            rational_ob = RationalObject(rational[1], rational[2])
            expression_data.append(rational_ob)
        
        return expression_data


    def main_process(self):
        """
        Checks operators in expression_data and directs it to other methods based on operator
        Negative sign always distributed first if present, no subtraction
        """
        print("")
        print("")
        self.print_out_expression(self.expression_data, "")


        no_neg_expression_data = simp_negatives(self.expression_data)
        if no_neg_expression_data != self.expression_data:
            self.print_out_expression(no_neg_expression_data, "Simplify and distribute negatives")

        if len(no_neg_expression_data) <= 2:
            processed_expression_data = self.simp(no_neg_expression_data)
        
        if "/" in no_neg_expression_data:
            processed_expression_data = self.divide(no_neg_expression_data)
        
        if "*" in no_neg_expression_data:
            processed_expression_data = self.multiply(no_neg_expression_data)
        
        if "+" in no_neg_expression_data:
            processed_expression_data = self.add(no_neg_expression_data)
        
        final_expression_data = cancel_lc(processed_expression_data)

        if final_expression_data != processed_expression_data:
            self.print_out_expression(final_expression_data, "completely simplify")


    def simp(self, input_expression_data):
        """
        Simplifies a rational expression - factors and cancels, then returns the new expression_data
        Built in a way that makes it reusable for other operator methods that also factor and cancel
        """
        
        factored_expression_data = factor_rationals(input_expression_data)
        self.print_out_expression(factored_expression_data, "factor")

        canceled_expression_data = cancel_factors(factored_expression_data)
        self.print_out_expression(canceled_expression_data, "cancel")
        
        return canceled_expression_data
        
    def add(self, input_expression_data):
        """
        Adds two rationals together - factors the denomenator, finds and applies the lcd, combines the expression, then
        returning new expression_data
        """
        factored_expression_data = factor_rationals(input_expression_data, factor_numerator=False)
        self.print_out_expression(factored_expression_data, "factor denomenator")
    
        lcd_expression_data = apply_lcd(factored_expression_data, expression = True)
        self.print_out_expression(lcd_expression_data, "find and apply lcd")

        expanded_expression_data = expand_numerator(lcd_expression_data)
        self.print_out_expression(expanded_expression_data, "")

        added_expression_data = final_add(expanded_expression_data)
        self.print_out_expression(added_expression_data, "add numerators")

        return added_expression_data

    def multiply(self, input_expression_data):
        """
        Multiples two rationals together - factors and cancels and multiplies, then returns new expression_data
        Calls simp() to factor and cancel
        """
        canceled_expression_data = self.simp(input_expression_data)
        
        muliplied_expression_data = multiply_factors(canceled_expression_data)
        self.print_out_expression(muliplied_expression_data, "multiply numerator and denomenator")

        return muliplied_expression_data

    def divide(self, input_expression_data):
        """
        Divides two rationals together - flip and factors and cancels and multiplies
        Calls multiply() to multiply after flipping and changing signs
        """
        divisor = input_expression_data[2]
        flipped_divisor = RationalObject(divisor.denomenator, divisor.numerator)
        flipped_expression_data = [input_expression_data[0]]+ ["*"] + [flipped_divisor]
        
        self.print_out_expression(flipped_expression_data, "flip divisor and change sign")

        canceled_expression_data = self.multiply(flipped_expression_data)
        
        return canceled_expression_data

    def print_out_expression(self, expression_data, message):
        print("")
        print("")
        sympy_str = get_sympy_str(expression_data)
        print(message)
        pretty_print(sympy_str)

    @classmethod
    def from_latex(cls, latex_str):
        #raw_latex_str = r"{}".format(latex_str)
        latex_str = subsitute(r"\\left|\\right", "", latex_str)
        sympy_str = str(sympify(parse_latex(latex_str)))
        return cls(sympy_str)








class Equation(Expression):
    def __init__(self, input_str):
        print(input_str)
        self.expression_data = self.expression_data_version(sympify(input_str))
        self.sympy_ob = sympify(input_str)
    
    def main_process(self):
        print("")
        print("")
        self.print_out_equation(self.expression_data, "")
        
        no_neg_expression_data = simp_negatives(self.expression_data)
        if no_neg_expression_data != self.expression_data:
            self.print_out_equation(no_neg_expression_data, "Simplify and distribute negatives")
    
        factored_expression_data = factor_rationals(no_neg_expression_data)
        self.print_out_equation(factored_expression_data, "factor")

        lcd_expression_data = apply_lcd(factored_expression_data, expression=False)
        self.print_out_equation(lcd_expression_data, "find and multiply all numerators by lcd")
        
        canceled_expression_data = cancel_equations(lcd_expression_data)
        self.print_out_equation(canceled_expression_data, "cancel out to get rid of denomenators")

        canceled_sympy = self.sympy_version(canceled_expression_data)
        variable = str(list(canceled_sympy.free_symbols)[0])
        possible_solutions = solve(canceled_sympy)
        print("solve equation")
        print(variable + " = " + str(set(possible_solutions)))

        
        good_solutions = self.check_for_extraneous(variable, possible_solutions)
        print("")
        print("")
        print("Check for extraneous solutions by subbing values back in")
        print(variable + "=" + str(set(good_solutions)))
                    

    def check_for_extraneous(self, variable, possible_solutions):
        good_solutions = []
        for value in possible_solutions:
            #subbed_expression = subsitute(variable, str(value), str(self.sympy_ob)) 
            l = self.sympy_ob.lhs.subs(variable, value)
            r = self.sympy_ob.rhs.subs(variable, value)
            if str(l) != "zoo" and str(r) != "zoo":
                good_solutions.append(value)
        
        return good_solutions

    def expression_data_version(self, sympy_ob):
        left_hand_side, right_hand_side = sympy_ob.lhs, sympy_ob.rhs
        
        expression_data = self.input_to_expr(str(left_hand_side))
        expression_data.append("=")
        expression_data += self.input_to_expr(str(right_hand_side))

        return expression_data

    def sympy_version(self, expression_data):
        left_hand_side, right_hand_side = [], []

        index = expression_data.index("=")
        left_hand_side = expression_data[:index]
        right_hand_side = expression_data[index+1:]
        
        left_str, right_str = get_sympy_str(left_hand_side), get_sympy_str(right_hand_side)
        
        return sympify("Eq({},{})".format(left_str, right_str), evaluate= False)
    
    def print_out_equation(self, expression_data, message):
        print("")
        print("")
        print(message)
        sympy_data = self.sympy_version(expression_data)
        pretty_print(sympy_data)

        







class PFD(Equation):
    unknown_variables = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'F', 5: 'G', 6: 'H', 7: 'I', 8: 'J', 9: 'K', 10: 'L', 11: 'M',
                             12: 'N', 13: 'O', 14: 'P', 15: 'Q', 16: 'R', 17: 'S', 18: 'T', 19: 'U', 20: 'V', 21: 'W', 22: 'X', 23: 'Y', 24: 'Z'}

    def __init__(self, input_str):
        self.expression_data = self.input_to_expr(input_str)
    
    def main_process(self):
        self.print_out_expression(self.expression_data, "")

        no_neg_expression_data = simp_negatives(self.expression_data)
        if no_neg_expression_data != self.expression_data:
            self.print_out_expression(no_neg_expression_data, "Simplify and distribute negatives")
        
        divided_expression_data, quotient = self.check_improper(no_neg_expression_data)
        if divided_expression_data != no_neg_expression_data:
            self.print_out_expression(divided_expression_data, "Since the numerator has a larger degree than the denomenator, divide and use remainder to decompose fraction")
            print("")
            print("Remember quotient for end: {}".format(quotient))

        factored_expression_data = factor_rationals(divided_expression_data, factor_numerator=False)
        variable = sympify(get_sympy_str(factored_expression_data)).free_symbols.pop()
        self.print_out_expression(factored_expression_data, "factor denomenator")

        split_expression_data = self.create_split_vars(factored_expression_data)
        self.print_out_equation(split_expression_data, "split factors into denomenators of smaller fractions, putting unknown variables as the numerators")

        lcd_expression_data = apply_lcd(split_expression_data, expression=False)
        self.print_out_equation(lcd_expression_data, "find and multiply all numerators by lcd")
        
        canceled_expression_data = cancel_equations(lcd_expression_data)
        self.print_out_equation(canceled_expression_data, "cancel out to get rid of denomenators")
        
        expanded_expression_data = expand_numerator(canceled_expression_data)
        self.print_out_equation(expanded_expression_data, "distribute unknown values")

        system = self.create_system(expanded_expression_data, variable)
        print("")
        print("")
        print("create a system of equations based on the degrees")
        for i in system:
            pretty_print(i)

        print("")
        print("")
        print("solve for variables using any strategy")
        variable_solutions = self.solve_system(system)
        for key in variable_solutions.keys():
            print("{} = {}".format(key, variable_solutions[key]))

        final_expression_data = self.expression_data + ["="] + self.get_rhs_expression_data(split_expression_data)
        a = self.create_solved_expression(final_expression_data, variable_solutions, quotient)
        print(a)
        self.print_out_equation(a, "Sub in values for variables")
    
    def create_solved_expression(self, expression_data, variable_solutions, quotient=None):
        output = []
        for part in expression_data:
            if isinstance(part, (FactoredRationalObject)):
                numerator_str = part.get_n_str()[1:-1]

                if numerator_str in variable_solutions.keys():
                    matched_solution = variable_solutions[numerator_str]
                    
                    temp_numerator = subsitute("[A-Z]", "1", numerator_str)
                    a = sympify("(" + temp_numerator + "/" + part.get_d_str() + ")*" + str(matched_solution))
                    output += self.input_to_expr(str(a))
                    
            else:
                output.append(part)

        if quotient:
            index = output.index("=")
            output.insert(index+1, quotient)
            output.insert(index+2, "+")

        return output
                    

    def get_rhs_expression_data(self, expression_data):
        index = expression_data.index("=")
        return expression_data[index+1:]

    def solve_system(self, system):
        ordered_unknowns = list(PFD.unknown_variables.values())[:len(system)]
        solutions = list(linsolve(system, ordered_unknowns))[0]
        assigned_solution = {variable:solution for variable,solution in zip(ordered_unknowns, solutions)}
        print(assigned_solution)
        return assigned_solution
    
    def create_system(self, expression_data, variable):
        sympy_ob = self.sympy_version(expression_data)
        left_hand_side, right_hand_side = sympy_ob.lhs.args, sympy_ob.rhs.args
        
        system = []
        
        for l_term in left_hand_side:
            l_degree = int(l_term.as_powers_dict()[variable])

            new_right_side = self.create_system_helper(l_degree, right_hand_side, variable)
            new_left_side = str(sympify("{}/({}**{})".format(str(l_term), variable, l_degree)))
            
            system.append(sympify("Eq({},{})".format(new_left_side, "+".join(new_right_side))))
            
        return system
    
    
    def create_system_helper(self, l_degree, right_hand_side, variable):
        matching_degrees = []

        for r_term in right_hand_side:
            if int(r_term.as_powers_dict()[variable]) == l_degree:
                without_variable = str(sympify("{}/({}**{})".format(r_term, variable, l_degree)))
                matching_degrees.append(without_variable)

        return matching_degrees


    def create_split_vars(self, expression_data):
        factored_rational = expression_data[0]
        split_expression_data = [factored_rational, "="]
        for index, factor in enumerate(factored_rational.denomenator):
            split_expression_data.append(FactoredRationalObject([PFD.unknown_variables[index]], [factor]))
            if index != len(factored_rational.denomenator) - 1:
                split_expression_data.append("+")
        
        return split_expression_data

    def check_improper(self, expression_data):
        original_rational = expression_data[0]

        if degree(sympify(original_rational.numerator)) > degree(sympify(original_rational.denomenator)):
            numerator_polynomial, denomenator_polynomial = sympify(original_rational.numerator), sympify(original_rational.denomenator)
            quotient, remainder = div(numerator_polynomial, denomenator_polynomial)
            divided_expression_data = [RationalObject(str(remainder), original_rational.denomenator)]
            return divided_expression_data, str(quotient)
        
        return expression_data, None
        



class ComplexFractions(object):
    pass

test = {r" \frac{\left(n+2\right)}{10n^2+20n}":r"\frac{1}{10n}", r"\frac{\left(30n-24\right)}{54n^2}": r"\frac{\left(5n-4\right)}{9n^2}", r"\frac{81x}{18x^2+90}": r"\frac{9}{2x+10}", 
r"\frac{\left(x+40\right)}{2x^2+99x+760}": r"\frac{1}{2x+19}", r"\frac{\left(7n^2-36n-36\right)}{49n+42}\cdot\frac{\left(35n+42\right)}{30n+36}": r"\frac{\left(n-6\right)}{6}", 
r"\frac{\left(21n-49\right)}{7-3n}\cdot\frac{\left(5n^2+30n+25\right)}{35n+35}": r"-\left(n+5\right)", 
r"\frac{\left(8p^3-32p^2\right)}{5p^2+28p-49}\cdot\frac{\left(5p-7\right)}{8p^3-64p^2}": r"\frac{\left(p-4\right)}{\left(p+7\right)\left(p-8\right)}", 
r"\frac{\frac{\left(5x-40\right)}{25x+15}}{\frac{6x}{20x+12}}": r"\frac{2\left(x-8\right)}{3x}"}



test2 = {r"\frac{3}{x-1}+\frac{6x}{2x+3}" : r"\frac{\left(3\left(2x^2+3\right)\right)}{\left(x-1\right)\left(2x+3\right)}", r"\frac{7x}{x-5}-\frac{4}{5-x}": r"\frac{\left(7x+4\right)}{x-5}",
r"\frac{\left(x^2-12x+1\right)}{x+5}+\frac{\left(x^2-9\right)}{x-4}": "", r"\frac{4}{7x+2}+\frac{8}{6x-5}+\frac{\left(-3\right)}{14x-9}+\frac{17}{x-1}-\frac{1}{x}":""}

test3 = {r"\frac{2}{5}+\frac{4}{10x+5}=\frac{7}{2x+1}": "", r"\frac{10}{x^2-2x}+\frac{4}{x}=\frac{5}{x-2}": "", r"\frac{1}{6k^2}=\frac{1}{3k^2}-\frac{1}{k}": "",
r"\frac{1}{v}+\frac{\left(3v+12\right)}{v^2-5v}=\frac{\left(7v-56\right)}{v^2-5v}": "", r"\frac{1}{m^2-m}+\frac{1}{m}=\frac{5}{m^2-m}": "", r"\frac{\left(p+5\right)}{p^2+p}=\frac{1}{p^2+p}-\frac{\left(p-6\right)}{p+1}": ""}


test4 = {r"\frac{\left(x^2+16x-4\right)}{x^3-4x}": "", r"\frac{\left(x^3-4x^2-4x-9\right)}{x^2-5x-6}": "", r"\frac{\left(x+7\right)}{x^2-x-6}": "", r"\frac{\left(-5x-18\right)}{2x^2+11x-21}": "", r"-\frac{-2x+3}{x^2+x}": "", r"\frac{10402x^4-12313x^3+1145x^2+1441x+90}{588x^5-1288x^4+767x^3+23x^2-90x}": ""}

if __name__ == "__main__": 
    a = []
    for problem, answer in test.items():
        expression_ob = Expression.from_latex(problem)
        expression_ob.main_process()

    for problem, answer in test2.items():
        expression_ob = Expression.from_latex(problem)
        expression_ob.main_process()

    for problem, answer in test3.items():
        expression_ob = Equation.from_latex(problem)
        expression_ob.main_process()

    for problem, answer in test4.items():
        expression_ob = PFD.from_latex(problem)
        expression_ob.main_process()

