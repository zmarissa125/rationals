"""
Main file for the program
Did I write 800ish lines of code for 8 points? yes
"""
from collections import Counter
from re import findall, split, sub as subsitute
from sympy import (Eq, cancel, degree, div, evalf, expand,
                   factor, factor_list, latex, linsolve, pretty_print,
                   simplify, solve, sympify, UnevaluatedExpr)


from my_latex_parse import latex_to_data
from base_rationals import *


class Expression(object):
    """
    Takes in rational expression, processes it, and outputs an answer and instructions
    Can only take in one operation at a time (excluding negative sign)
    
    Class and instance variables:
    expression_data is the broken down expression, a list of operators and RationalObjects 
                        (all variables that end in expression_data are in this form)
    full_output is a list of dictionaries that includes instructions and the modified expression as a latex string
            ex. [{"message": _________________, "latex": _______________}, {"message": _________________, "latex": _______________}, ...]
    


    
    Methods:
    Three constructors - standard __init__(), from_latex(), and input_to_expr()
            from_latex() preferred as the constructor, other methods are more prone to error and misinterpretation
    
    data_to_sympy_expression(): Turns expression_data into printable sympy object
    
    main_process(): takes expression_data and directs it to functions based on operator
    
    simp(): Takes in expression_data and simplifies the expression
    
    add(): Takes in expression_data and adds the rationals
    
    multiply(): Takes in expression_data and multiplies the rationals
    
    divide(): Takes in expression_data and divides the rationals

    print_out_expression(): Takes in expression data and message, printing both out and logging them in full_output
    """
    
    def __init__(self, expression_data):
        """
        Creates Expression instance and sets expression_data variable and full_output variable
        """

        self.expression_data = expression_data
        self.full_output = []

    def data_to_sympy_expression(self, expression_data):
        """
        Turns expression data into printable sympy object
        """
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
        Negative sign always distributed first if present, no subtraction function

        returns full output
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
        
        no_int_expression_data = simp_ints(processed_expression_data)
        final_expression_data = cancel_multiplication_factors(no_int_expression_data)
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

        canceled_expression_data = cancel_multiplication_factors(factored_expression_data)
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

        simplified_expression_data = self.simp(added_expression_data)

        return simplified_expression_data

    def multiply(self, input_expression_data):
        """
        Multiples two rationals together - factors and cancels and multiplies, then returns new expression_data
        Calls simp() to factor and cancel
        """
        canceled_expression_data = self.simp(input_expression_data)
        
        return canceled_expression_data

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
        """
        prints out the message and the pretty printed version of expression_data

        also logs the message and latex of the expression_data in full_output
        """
        print("")
        print("")
        sympy_str = self.data_to_sympy_expression(expression_data)
        print(message)
        pretty_print(sympy_str)

        latex_str = latex(sympify(sympy_str))
        self.full_output.append({"message": message, "latex": latex_str})  



    @classmethod
    def input_to_expr(cls, input_str):
        """
        Alternative constructor for Expression - creates instance of Expression with an string input 


        input_str must be in this form: ((numerator1)/(denomenator1)) operator ((numerator2)/(denomenator2)), 
                multiplication must be denoted with *, and must appear between all items in a term
                exponents denoted with **


        NOTE: from_latex() is preffered as a constructor, as input_to_expr can only interpret 95% of cases
        """

        expression_data = []
        broken_down = findall("\s?(-|\+|\*|/)?\s?\(?\(?\(?\(?(\(.+?\)|[0-9]*|.+?)/([a-z]*\*\*[0-9]*|\(.+?\)|[a-z]+?|[0-9]*|.*?|)\)?\)?\)?", input_str) 

        for rational in broken_down:
            if rational[0]:
                expression_data.append(rational[0])
            rational_ob = RationalObject(rational[1], rational[2])
            expression_data.append(rational_ob)

        return cls(expression_data)


    @classmethod
    def from_latex(cls, latex_str):
        """
        Alternative constructor for Expression - creates instace of Expression with a latex string
        """
        expression_data = latex_to_data(latex_str)
        return cls(expression_data)










class Equation(Expression):
    """
    Takes in rational eqaution (in expression_data format), processes it, and outputs an answer and instructions
    Inherits from Expression, but adds additional functions
        
    Same as Expression class:
                Class and instance variables:
                expression_data is the broken down expression, a list of operators and RationalObjects 
                        (all variables that end in expression_data are in this form)
                full_output is a list of dictionaries that includes instructions and the modified expression as a latex string
                        ex. [{"message": _________________, "latex": _______________}, {"message": _________________, "latex": _______________}, ...]
                
                Class methods:
                Three constructors - standard __init__(), from_latex(), and input_to_expr()
                from_latex() preferred as the constructor, other methods are more prone to error and misinterpretation


    
    Additional Methods:

    main_process(): overwritten from Expression class, takes expression_data and directs it to other functions to solve the equation

    check_for_extraneous(): goes through list of possible solutions and plugs them into the orignal equation, returns a list a solutions

    
    Since equations in Sympy are formated different from expressions, functions data_to_sympy(), str_to_sympy_equation(), and print_out_equation() needed for easy manipuation

    data_to_sympy_equation(): takes in expression_data and creates a sympy Equality object
    
    str_to_sympy_equation(): takes in a equation as a string and turns it into a sympy Equality object - mainly used for printing out solutions
     
    print_out_equation(): takes in expression_data and message to print them out into console, also logs them into full_output variable - used when equation needs to be printed
    """
    def __init__(self, expression_data):
        """
        Initiates Equation instance by calling __init__ of Expression and setting sympy_ob
        """
        super().__init__(expression_data)
        
        self.sympy_ob = self.data_to_sympy_equation(expression_data)
        

    def main_process(self):

        """
        Calls other functions and methods to solve equation from expression_data
        Returns full_output
        """
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
        
        canceled_expression_data = cancel_addition_factors(lcd_expression_data)
        self.print_out_equation("cancel out to get rid of denomenators", canceled_expression_data)

        canceled_sympy = self.data_to_sympy_equation(canceled_expression_data)
        variable = str(list(canceled_sympy.free_symbols)[0])
        possible_solutions = solve(canceled_sympy)
        self.print_out_variable(variable, possible_solutions, "solve equation for possible solutions")

        
        good_solutions = self.check_for_extraneous(variable, possible_solutions)
        self.print_out_variable(variable, good_solutions, "Check for extraneous solutions to find final answer")


        return self.full_output
    
    def check_for_extraneous(self, variable, possible_solutions):
        """
        checks for extraneous solutions from possible solutions
        returns solutions 
        """
        good_solutions = []
        for value in possible_solutions:
            l = self.sympy_ob.lhs.subs(variable, value)
            r = self.sympy_ob.rhs.subs(variable, value)
            if str(l) != "zoo" and str(r) != "zoo":
                good_solutions.append(value)
        
        return good_solutions


    def data_to_sympy_equation(self, expression_data):
        """
        turns expression_data into a sympy equation
        """

        index = expression_data.index("=")
        left_hand_side = expression_data[:index]
        right_hand_side = expression_data[index+1:]
        
        left_str, right_str = self.data_to_sympy_expression(left_hand_side), self.data_to_sympy_expression(right_hand_side)
        return sympify("Eq({},{})".format(left_str, right_str), evaluate= False)

    def str_to_sympy_equation(self, equation_str):
        """
        turns an equation string into a sympy equation
        """
        index = equation_str.index("=")
        left_str = equation_str[:index]
        right_str = equation_str[index + 1:]
        return sympify("Eq({},{})".format(left_str, right_str), evaluate= False)

    def print_out_variable(self, variable, solutions, message):
        """
        Logs variable solution equations in full_output and prints in console 
        """
        for index, solution in enumerate(solutions):
            solutions_str = "{} = {}".format(variable, str(solution))
            sympy_ob = self.str_to_sympy_equation(solutions_str)
            if index == 0:

                self.print_out_equation(message, sympy_ob = sympy_ob)
            else:
                self.print_out_equation("", sympy_ob = sympy_ob)


    def print_out_equation(self, message, expression_data=None, sympy_ob = None):
        """
       logs equation and prints out equation in console
       can be from expression_data or a sympy equation object
        """
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
    Takes a rational (in expression_data format) and does a partial fraction decomposition if possible - can only take one unknown variable in initial expression
    Inherits from Equation Class, and as a result also inherits from Expression class


    Same as Expression class and Equation class:
                Class and instance variables:
                expression_data is the broken down expression, a list of operators and RationalObjects 
                        (all variables that end in expression_data are in this form)
                full_output is a list of dictionaries that includes instructions and the modified expression as a latex string
                        ex. [{"message": _________________, "latex": _______________}, {"message": _________________, "latex": _______________}, ...]
                
                Class methods:
                Three constructors - standard __init__(), from_latex(), and input_to_expr()
                from_latex() preferred as the constructor, other methods are more prone to error and misinterpretation

                data_to_sympy(): takes in expression_data and creates a sympy Equality object
    
                str_to_sympy_equation(): takes in a equation as a string and turns it into a sympy Equality object - mainly used for printing out solutions

                print_out_expression(): Takes in expression data and message, printing both out and logging them in full_output - used when expression is needed to be printed

                print_out_equation(): Takes in expression data and message, printing both out and logging them in full_output - used when equation is needed to be printed

    
    Additional variables:
    unknown_vatiables is a dictionary of numbers corresponding to letter - makes creating system of equations easier



    Additional methods:
    
    main_process(): overwritten from Equation class, takes expression_data and directs it to other functions to decompose the function

    check_improper(): checks whether rational is improper, dividing it and returning the remainder and quotient

    create_split_vars(): splits up the rational's factored denomenator, breaking down into smaller fractions being added

    create_system(): creates a system of equations by checking degrees on both sides of the equation
        create_system_helper(): helper function that aids create_system()

    solve_system(): solves the system of equations

    get_rhs_expression_data(): returns the right hand side of equation in expression_data format

    create_solved_system(): puts everything together, returning final answer in expression_data format
    """


    unknown_variables = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'F', 5: 'G', 6: 'H', 7: 'I', 8: 'J', 9: 'K', 10: 'L', 11: 'M',
                             12: 'N', 13: 'O', 14: 'P', 15: 'Q', 16: 'R', 17: 'S', 18: 'T', 19: 'U', 20: 'V', 21: 'W', 22: 'X', 23: 'Y', 24: 'Z'}

    def __init__(self, expression_data):
        """
        Creates Expression instance and sets expression_data variable and full_output variable
        """
        self.expression_data = expression_data
        self.full_output = []

    def main_process(self):
        """
        Uses expression_data with a rational in it and decomposes it, returns all the steps in full_output
        """
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
        
        canceled_expression_data = cancel_addition_factors(lcd_expression_data)
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
        """ 
        checks if the rational in expression_data is improper by checking degrees
        if it is improper it returns expression_data wih a RationalObject with remaimder as numerator instead, also returns the quotient
        If not improper, original expression_data is returned
        """
        original_rational = expression_data[0]

        if degree(sympify(original_rational.numerator)) > degree(sympify(original_rational.denomenator)):
            numerator_polynomial, denomenator_polynomial = sympify(original_rational.numerator), sympify(original_rational.denomenator)
            quotient, remainder = div(numerator_polynomial, denomenator_polynomial)
            divided_expression_data = [RationalObject(str(remainder), original_rational.denomenator)]
            return divided_expression_data, str(quotient)
        
        return expression_data, None



    def create_split_vars(self, expression_data):
        """
        Takes in expression_data, and uses factors to decompose, putting unknwns in the numerator
        returns modified expression_data
        """
        factored_rational = expression_data[0]
        split_expression_data = [factored_rational, "="]
        for index, factor in enumerate(factored_rational.denomenator):
            split_expression_data.append(FactoredRationalObject([PFD.unknown_variables[index]], [factor]))
            if index != len(factored_rational.denomenator) - 1:
                split_expression_data.append("+")
        
        return split_expression_data



    def create_system(self, expression_data, variable):
        """
        Creates a system of equations from expression_data by finding mathcing degrees on both sides, returing system - a list of equations
        """
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
        """
        helper function for create_system, finds items on right side of equation with teh same degree as the term on the left
        """
        matching_degrees = []

        for r_term in right_hand_side:
            if int(r_term.as_powers_dict()[variable]) == l_degree:
                without_variable = str(sympify("{}/({}**{})".format(r_term, variable, l_degree)))
                matching_degrees.append(without_variable)

        return matching_degrees


    def solve_system(self, system):
        """
        solves system with sympy, returning a dictionary with unknowns and their solutions
        """
        ordered_unknowns = list(PFD.unknown_variables.values())[:len(system)]
        solutions = list(linsolve(system, ordered_unknowns))[0]
        assigned_solution = {variable:solution for variable,solution in zip(ordered_unknowns, solutions)}
        return assigned_solution



    def get_rhs_expression_data(self, expression_data):
        """
        returns the expression_data of the right hand side of input expression_data with equation
        """
        index = expression_data.index("=")
        return expression_data[index+1:]
    
    

    def create_solved_expression(self, expression_data, variable_solutions, quotient=None):
        """
        Puts solution dictionary, expression_data, and possibe quotient (if improper) together
        Replaces solutions into the unknowns, adding the quotient if applicable
        Returns modified expression_data 
        """
        output = []
        for part in expression_data:
            if isinstance(part, (FactoredRationalObject)):
                numerator_str = part.get_n_str()[1:-1]

                if numerator_str in variable_solutions.keys():
                    matched_solution = variable_solutions[numerator_str]
                    
                    temp_numerator = subsitute("[A-Z]", "1", numerator_str)
                    mini_expression_data = [RationalObject(temp_numerator, part.get_d_str()) * RationalObject(str(matched_solution), 1)]
            
                    output += mini_expression_data
                    
            else:
                output.append(part)

        if quotient:
            index = output.index("=")
            output.insert(index+1, quotient)
            output.insert(index+2, "+")

        return output










class ComplexFractions(Expression):
    """
    Takes in expression with complex fractions (in expression_data format), processes it, and outputs an answer and instructions
            expression data must have ComplexRationalObjects
    Inherits from Expression, but adds additional functions
        
    Same as Expression class:
                Class and instance variables:
                expression_data is the broken down expression, a list of operators and RationalObjects 
                        (all variables that end in expression_data are in this form)
                full_output is a list of dictionaries that includes instructions and the modified expression as a latex string
                        ex. [{"message": _________________, "latex": _______________}, {"message": _________________, "latex": _______________}, ...]
                
                Class methods:
                Three constructors - standard __init__(), from_latex(), and input_to_expr()

    Additional methods:
    main_process(): overwritten from Expression class, takes expression_data and directs it to other functions to simplify the complex fractions
            calls Expression classes main process to process expression_data after complex fractions have been simplified

    complex_wrapper_function(): takes in expression_data and function that operates on expression_data, to run it on both the numerator and denomenator of a ComplexRationalObject
    
    find_complex_lcd(): takes in ComplexRationalObject, returns lcd for the complex fraction

    apply_complex_lcd(): takes in expression data and finds and applies lcd for each ComplexRationalObject, returns modified expression_data

    not_complex_anymore(): takes in expression data with simplified ComplexRationalObjetcs, returns expression data with FactoredRationalObject

    from_latex(): modified from Expression, mostly same, but complex fractions allowed
    """
    
    def main_process(self):
        """
        Uses expression_data and directs it to other functions to simplify complex fractions, logging steps and latex in full_output
        returns full_output
        """
        self.print_out_expression(self.expression_data, "")
        
        no_neg_expression_data = self.complex_wrapper_function(self.expression_data, distribute_negatives)
        if no_neg_expression_data != self.expression_data:
            self.print_out_expression(no_neg_expression_data, "distribute the numerator's and denomenator's negatives")

        factored_expression_data = self.complex_wrapper_function(no_neg_expression_data, factor_rationals, factor_numerator=False)
        self.print_out_expression(factored_expression_data, "factor all sub denomenators")
        
        lcd_expression_data = self.apply_complex_lcd(factored_expression_data)
        self.print_out_expression(lcd_expression_data, "find the LCDs for each complex fraction, and multiply each sub numerator and denomenator by it")

        canceled_expression_data = self.complex_wrapper_function(lcd_expression_data, cancel_addition_factors)
        self.print_out_expression(canceled_expression_data, "cancel out the sub numerators and subdenomenators to get rid of denomenators")

        expanded_expression_data = self.complex_wrapper_function(canceled_expression_data, expand_numerator)
        self.print_out_expression(expanded_expression_data, "Work out the numerators and denomenators")

        added_expression_data = self.complex_wrapper_function(expanded_expression_data, final_add)
        self.print_out_expression(added_expression_data, "")

        self.expression_data =  self.not_complex_anymore(added_expression_data)
        super().main_process()


        return self.full_output
    
    def complex_wrapper_function(self, expression_data, func, **kwargs):
        """
        takes in expression_data, function, and possible keyword arguments - maximizes reusability :)
        runs the function on both numerator and denomenator of COmplexRationalObject (since both are expression_data)
        returns modified expression_data
        """
        output = []
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                new_numerator = func(part.numerator, **kwargs)
                new_denomenator = func(part.denomenator, **kwargs)
                output.append(ComplexRationalObject(new_numerator, new_denomenator))
            else:
                output.append(part)

        return output


    def find_complex_lcd(self, rational_ob):
        """
        finds the lcd of a ComplexRationalObject by finding lcd of numerator and lcd of denomenator, then finding the intersection between them
        returns lcd of the ComplexRationalObject
        """
        lcd = []
        
        numerator_lcd = find_lcd(rational_ob.numerator)
        denomenator_lcd = find_lcd(rational_ob.denomenator)
        lcd += list((Counter(denomenator_lcd)-Counter(lcd)).elements())
        lcd += list((Counter(numerator_lcd)-Counter(lcd)).elements()) 
        
        return lcd

    
    def apply_complex_lcd(self, expression_data):
        """
        finds and applies lcd to each ComplexRationalObject
        """
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

    def not_complex_anymore(self, expression_data):
        """
        turns simplified ComplexRationalObjects into FactoredRationalObjects
        """
        output = []
        for part in expression_data:
            if isinstance(part, ComplexRationalObject):
                new_numerator = part.numerator[0].numerator[0]
                new_denomenator = part.denomenator[0].numerator[0]
            
                output.append(FactoredRationalObject.from_factored_str(new_numerator, new_denomenator, factor_numerator=True))
            else:
                output.append(part)
        return output



    @classmethod
    def from_latex(cls, latex_str):
        """
        modifies from_latex inherited from Expression, enabling latex_parser to create ComplexRationalObjects
        """
        expression_data = latex_to_data(latex_str, complex_frac=True)
        return cls(expression_data)

