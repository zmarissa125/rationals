from collections import Counter
from re import findall, split
from re import sub as subsitute

from sympy import (Eq, cancel, degree, div, evalf, expand,
                   factor, factor_list, latex, linsolve, pretty_print,
                   simplify, solve, sympify)

from my_latex_parse import latex_to_data
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
    
    def __init__(self, expression_data):
        """
        Creates Expression instance and sets expression_data variable, prints out input expression
         
        input_str must be in this form: ((numerator1)/(denomenator1)) operator ((numerator2)/(denomenator2)), 
                multiplication must be denoted with *, and must appear between all items in a term
                exponents denoted with **
        """

        self.expression_data = expression_data
        self.full_output = []

    def data_to_sympy_expression(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, (RationalObject, FactoredRationalObject, ComplexRationalObject)):
                output.append(str(part))
            else:
                output.append(part)

        return sympify("".join(output), evaluate=False)


    def main_process(self):
        """
        Checks operators in expression_data and directs it to other methods based on operator
        Negative sign always distributed first if present, no subtraction
        """
        print("")
        print("")
        self.print_out_expression(self.expression_data, "")


        no_neg_expression_data = distribute_negatives(self.expression_data)
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
        
        final_expression_data = simp_ints(processed_expression_data)

        if final_expression_data != processed_expression_data:
            self.print_out_expression(final_expression_data, "completely simplify")

        return self.full_output


        
    def simp(self, input_expression_data):
        """
        Simplifies a rational expression - factors and cancels, then returns the new expression_data
        Built in a way that makes it reusable for other operator methods that also factor and cancel
        """
        
        factored_expression_data = factor_rationals(input_expression_data)
        self.print_out_expression(factored_expression_data, "factor")

        canceled_expression_data = cancel_expression_factors(factored_expression_data)
        self.print_out_expression(canceled_expression_data, "cancel")
        
        return canceled_expression_data
        
    def add(self, input_expression_data):
        """
        Adds two rationals together - factors the denomenator, finds and applies the lcd, combines the expression, then
        returning new expression_data
        """
        factored_expression_data = factor_rationals(input_expression_data, factor_numerator=False)
        self.print_out_expression(factored_expression_data, "factor denomenator")

        lcd = find_lcd(factored_expression_data)
        lcd_expression_data = apply_lcd(factored_expression_data, lcd, expression = True)
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
        
        muliplied_expression_data = final_multiply(canceled_expression_data)
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
        sympy_str = self.data_to_sympy_expression(expression_data)
        print(message)
        pretty_print(sympy_str)

        latex_str = latex(sympify(sympy_str))
        self.full_output.append({"message": message, "latex": latex_str})  


    @classmethod
    def from_latex(cls, latex_str):
        expression_data = latex_to_data(latex_str)
        return cls(expression_data)















class Equation(Expression):
    """
    
    """
    def __init__(self, expression_data):
        super().__init__(expression_data)
        
        self.sympy_ob = self.data_to_sympy_equation(expression_data)
        

    def main_process(self):
        print("")
        print("")
        self.print_out_equation("", self.expression_data)
        
        no_neg_expression_data = distribute_negatives(self.expression_data)
        if no_neg_expression_data != self.expression_data:
            self.print_out_equation("Simplify and distribute negatives", no_neg_expression_data)
    
        factored_expression_data = factor_rationals(no_neg_expression_data)
        self.print_out_equation("factor", factored_expression_data)

        lcd = find_lcd(factored_expression_data)
        lcd_expression_data = apply_lcd(factored_expression_data, lcd, expression=False)
        self.print_out_equation("find and multiply all numerators by lcd", lcd_expression_data)
        
        canceled_expression_data = self.cancel_equation_factor(lcd_expression_data)
        self.print_out_equation("cancel out to get rid of denomenators", canceled_expression_data)

        canceled_sympy = self.data_to_sympy_equation(canceled_expression_data)
        variable = str(list(canceled_sympy.free_symbols)[0])
        possible_solutions = solve(canceled_sympy)
        for index, solution in enumerate(possible_solutions):
            solutions_str = "{} = {}".format(variable, str(solution))
            sympy_ob = self.str_to_sympy_equation(solutions_str)
            if index == 0:

                self.print_out_equation("solve equation", sympy_ob = sympy_ob)
            else:
                self.print_out_equation("", sympy_ob = sympy_ob)

        
        good_solutions = self.check_for_extraneous(variable, possible_solutions)
        
        for index, solution in enumerate(good_solutions):
            solutions_str = "{} = {}".format(variable, str(solution))
            sympy_ob = self.str_to_sympy_equation(solutions_str)
            if index == 0:

                self.print_out_equation("Check for extraneous solutions to find final answer", sympy_ob = sympy_ob)
            else:
                self.print_out_equation("", sympy_ob = sympy_ob)


        return self.full_output

    
    def data_to_sympy_equation(self, expression_data):

        index = expression_data.index("=")
        left_hand_side = expression_data[:index]
        right_hand_side = expression_data[index+1:]
        
        left_str, right_str = self.data_to_sympy_expression(left_hand_side), self.data_to_sympy_expression(right_hand_side)
        return sympify("Eq({},{})".format(left_str, right_str), evaluate= False)

    def str_to_sympy_equation(self, equation_str):
        index = equation_str.index("=")
        left_str = equation_str[:index]
        right_str = equation_str[index + 1:]
        return sympify("Eq({},{})".format(left_str, right_str), evaluate= False)

    def cancel_equation_factor(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, FactoredRationalObject):
                new_n = list((Counter(part.numerator)-Counter(part.denomenator)).elements())
                new_d = list((Counter(part.denomenator)-Counter(part.numerator)).elements())
                output.append(FactoredRationalObject(new_n, new_d))
            else:
                output.append(part)

        return output
    

    def check_for_extraneous(self, variable, possible_solutions):
        good_solutions = []
        for value in possible_solutions:
            #subbed_expression = subsitute(variable, str(value), str(self.sympy_ob)) 
            l = self.sympy_ob.lhs.subs(variable, value)
            r = self.sympy_ob.rhs.subs(variable, value)
            if str(l) != "zoo" and str(r) != "zoo":
                good_solutions.append(value)
        
        return good_solutions
    
    def print_out_equation(self, message, expression_data=None, sympy_ob = None):
        print("")
        print("")
        if expression_data:
            sympy_data = self.data_to_sympy_equation(expression_data)
        if sympy_ob != None:
            sympy_data = sympy_ob
        print(message)
        pretty_print(sympy_data)



        latex_str = latex(sympify(sympy_data))
        self.full_output.append({"message": message, "latex": latex_str})  
        

























class PFD(Equation):
    """
    """
    unknown_variables = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'F', 5: 'G', 6: 'H', 7: 'I', 8: 'J', 9: 'K', 10: 'L', 11: 'M',
                             12: 'N', 13: 'O', 14: 'P', 15: 'Q', 16: 'R', 17: 'S', 18: 'T', 19: 'U', 20: 'V', 21: 'W', 22: 'X', 23: 'Y', 24: 'Z'}

    def __init__(self, expression_data):
        self.expression_data = expression_data
        self.full_output = []

    def main_process(self):
        self.print_out_expression(self.expression_data, "")

        no_neg_expression_data = distribute_negatives(self.expression_data)
        if no_neg_expression_data != self.expression_data:
            self.print_out_expression(no_neg_expression_data, "Simplify and distribute negatives")
        
        divided_expression_data, quotient = self.check_improper(no_neg_expression_data)
        if divided_expression_data != no_neg_expression_data:
            self.print_out_expression(divided_expression_data, "Since the numerator has a larger degree than the denomenator, divide and use remainder to decompose fraction")
            print("")
            print("Remember quotient for end: {}".format(quotient))

        factored_expression_data = factor_rationals(divided_expression_data, factor_numerator=False)
        variable = sympify(self.data_to_sympy_expression(factored_expression_data)).free_symbols.pop()
        self.print_out_expression(factored_expression_data, "factor denomenator")

        split_expression_data = self.create_split_vars(factored_expression_data)
        self.print_out_equation("split factors into denomenators of smaller fractions, putting unknown variables as the numerators", expression_data = split_expression_data)

        lcd = find_lcd(split_expression_data)
        lcd_expression_data = apply_lcd(split_expression_data, lcd, expression=False)
        self.print_out_equation("find and multiply all numerators by lcd", expression_data = lcd_expression_data)
        
        canceled_expression_data = self.cancel_equation_factor(lcd_expression_data)
        self.print_out_equation("cancel out to get rid of denomenators", expression_data = canceled_expression_data)
        
        expanded_expression_data = expand_numerator(canceled_expression_data)
        self.print_out_equation("distribute unknown values", expression_data = expanded_expression_data)

        system = self.create_system(expanded_expression_data, variable)

        for index, equation in enumerate(system):
            if index == 0:
                self.print_out_equation("create a system of equations based on the degrees", sympy_ob = equation)
            else:
                self.print_out_equation("", sympy_ob= equation)

        
        variable_solutions = self.solve_system(system)
        for index, key in enumerate(variable_solutions.keys()):
            equation_str = "{} = {}".format(key, variable_solutions[key])
            sympy_ob = self.str_to_sympy_equation(equation_str)
            if index == 0:
                self.print_out_equation("solve for variables using any strategy", sympy_ob = sympy_ob)
            else:
                self.print_out_equation("", sympy_ob= sympy_ob)

        final_expression_data = self.expression_data + ["="] + self.get_rhs_expression_data(split_expression_data)
        a = self.create_solved_expression(final_expression_data, variable_solutions, quotient)
        self.print_out_equation("Sub in values for variables", a)
    
        return self.full_output



    def check_improper(self, expression_data):
        original_rational = expression_data[0]

        if degree(sympify(original_rational.numerator)) > degree(sympify(original_rational.denomenator)):
            numerator_polynomial, denomenator_polynomial = sympify(original_rational.numerator), sympify(original_rational.denomenator)
            quotient, remainder = div(numerator_polynomial, denomenator_polynomial)
            divided_expression_data = [RationalObject(str(remainder), original_rational.denomenator)]
            return divided_expression_data, str(quotient)
        
        return expression_data, None



    def create_split_vars(self, expression_data):
        factored_rational = expression_data[0]
        split_expression_data = [factored_rational, "="]
        for index, factor in enumerate(factored_rational.denomenator):
            split_expression_data.append(FactoredRationalObject([PFD.unknown_variables[index]], [factor]))
            if index != len(factored_rational.denomenator) - 1:
                split_expression_data.append("+")
        
        return split_expression_data



    def create_system(self, expression_data, variable):
        sympy_ob = self.data_to_sympy_equation(expression_data)
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


    def solve_system(self, system):
        ordered_unknowns = list(PFD.unknown_variables.values())[:len(system)]
        solutions = list(linsolve(system, ordered_unknowns))[0]
        assigned_solution = {variable:solution for variable,solution in zip(ordered_unknowns, solutions)}
        return assigned_solution



    def get_rhs_expression_data(self, expression_data):
        index = expression_data.index("=")
        return expression_data[index+1:]
    
    

    def create_solved_expression(self, expression_data, variable_solutions, quotient=None):
        output = []
        for part in expression_data:
            if isinstance(part, (FactoredRationalObject)):
                numerator_str = part.get_n_str()[1:-1]

                if numerator_str in variable_solutions.keys():
                    matched_solution = variable_solutions[numerator_str]
                    
                    temp_numerator = subsitute("[A-Z]", "1", numerator_str)
                    mini_expression_data = [RationalObject(temp_numerator, part.get_d_str()), "*", RationalObject(str(matched_solution), 1)]
                    
                    multiplied_expression_data = final_multiply(mini_expression_data)
                    output += multiplied_expression_data
                    
            else:
                output.append(part)

        if quotient:
            index = output.index("=")
            output.insert(index+1, quotient)
            output.insert(index+2, "+")

        return output












class ComplexFractions(Expression):
        
    def main_process(self):
        #find and appy lcd for numerator and denomenator
        #Cancel
        #turn to rational ob epxression?
        self.print_out_expression(self.expression_data, "")
        
        factored_expression_data = self.factor_complex(self.expression_data)
        self.print_out_expression(factored_expression_data, "factor all sub denomenators")
        
        lcd_expression_data = self.apply_complex_lcd(factored_expression_data)
        self.print_out_expression(lcd_expression_data, "find the LCDs for each complex fraction, and multiply each sub numerator and denomenator by it")

        canceled_expression_data = self.cancel_complex_factors(lcd_expression_data)
        self.print_out_expression(canceled_expression_data, "cancel out the sub numerators and subdenomenators to get rid of denomenators")

        expanded_expression_data = self.expand_complex(canceled_expression_data)
        self.print_out_expression(expanded_expression_data, "Work out the numerators and denomenators")

        added_expression_data = self.final_add_complex(expanded_expression_data)
        self.print_out_expression(added_expression_data, "")

        self.expression_data =  self.not_complex_anymore(added_expression_data)
        print(self.expression_data)
        new =  super().main_process()


        return self.full_output



    def factor_complex(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                new_numerator = factor_rationals(part.numerator, factor_numerator=False)
                new_denomenator = factor_rationals(part.denomenator, factor_numerator = False)
                output.append(ComplexRationalObject(new_numerator, new_denomenator))
            else:
                output.append(part)

        return output

    def find_complex_lcd(self, rational_ob):
        lcd = []
        
        numerator_lcd = find_lcd(rational_ob.numerator)
        denomenator_lcd = find_lcd(rational_ob.denomenator)

        lcd += list((Counter(denomenator_lcd)-Counter(numerator_lcd)).elements())
        lcd += list((Counter(numerator_lcd)-Counter(denomenator_lcd)).elements()) 
        
        if not lcd:
            lcd = numerator_lcd
        
        return lcd

    
    def apply_complex_lcd(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                lcd = self.find_complex_lcd(part)
                new_numerator = apply_lcd(part.numerator, lcd, expression=False)
                new_denomenator = apply_lcd(part.denomenator, lcd, expression=False)
                output.append(ComplexRationalObject(new_numerator, new_denomenator))
            else:
                output.append(part)

        return output

                 
    def cancel_complex_factors(self, expression_data):
        output = []
        
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                new_numerator = cancel_expression_factors(part.numerator)
                new_denomenator = cancel_expression_factors(part.denomenator)
                output.append(ComplexRationalObject(new_numerator, new_denomenator))
            else:
                output.append(part)

        return output

    
    def expand_complex(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                new_numerator = expand_numerator(part.numerator)
                new_denomenator = expand_numerator(part.denomenator)
                output.append(ComplexRationalObject(new_numerator, new_denomenator))
            else:
                output.append(part)

        return output

    def final_add_complex(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                new_numerator = final_add(part.numerator)
                new_denomenator = final_add(part.denomenator)
                output.append(ComplexRationalObject(new_numerator, new_denomenator))
            else:
                output.append(part)

        return output

    def not_complex_anymore(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                new_numerator = part.numerator[0].numerator[0]
                new_denomenator = part.denomenator[0].numerator[0]
                output.append(RationalObject(new_numerator, new_denomenator))
            else:
                output.append(part)
        return output


        

    @classmethod
    def from_latex(cls, latex_str):
        expression_data = latex_to_data(latex_str, complex_frac=True)
        return cls(expression_data)

