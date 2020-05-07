from sympy import factor, pretty_print, sympify, latex, cancel, expand, simplify
from sympy.parsing.latex import parse_latex
from re import sub as subsitute, findall
from collections import Counter
from rational_processes import RationalObject, FactoredRationalObject

class RationalBaseClass(object): #Still be in class??
    """
    Performs all basic functions necessary to solve rational functions
    """
    def get_all_nd(self, expression_data):
        numerators = []
        denomenators = []
        for part in expression_data:
            if isinstance(part, (RationalObject,FactoredRationalObject)):
                numerators += part.numerator
                denomenators += part.denomenator
        return numerators, denomenators
                
    def cancel_helper(self, n_or_d, comparison_list):
        canceled_n_or_d = []
        for factor in n_or_d:
            if factor not in comparison_list:
                canceled_n_or_d.append(factor)
            else:
                comparison_list.remove(factor)
        
        if not canceled_n_or_d:
            return [1], comparison_list
        
        return canceled_n_or_d, comparison_list

    def cancel_factors(self, expression_data):
        canceled_expression_data = []
        numerators, denomenators = self.get_all_nd(expression_data)
        for part in expression_data:
            
            if isinstance(part, FactoredRationalObject):
                canceled_n, denomenators = self.cancel_helper(part.numerator, denomenators)
                canceled_d, numerators = self.cancel_helper(part.denomenator, numerators)
                canceled_expression_data.append(FactoredRationalObject(canceled_n, canceled_d))
            else:
                canceled_expression_data.append(part)
        
        return canceled_expression_data
        
    def multiply_factors(self,expression_data):
        numerator_factors, denomenator_factors = self.get_all_nd(expression_data)
        return [FactoredRationalObject(numerator_factors, denomenator_factors)]
        
    def factor_rationals(self, expression_data, factor_numerator = True):
        factored_expression_data = []
        for part in expression_data: 
            
            if isinstance(part, RationalObject):
                factored_numerator, factored_denomenator = factor(part.numerator), factor(part.denomenator)
                factored_expression_data.append(FactoredRationalObject.from_factored_str(factored_numerator, factored_denomenator, factor_numerator))
            else:
                factored_expression_data.append(part)

        return factored_expression_data
            
    def cancel_lc(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, FactoredRationalObject):
                n_lc, n_no_lc, d_lc, d_no_lc = part.get_lc()
                a, b = n_lc, d_lc
                while b:
                    a, b = b, a%b
                output.append(FactoredRationalObject([int(n_lc/a)] + n_no_lc, [int(d_lc/a)] + d_no_lc))
            
            else:
                output.append(part)
        
        return output

    def apply_lcd(self, expression_data):
        lcd = self.find_lcd(expression_data)
        output = []
        for part in expression_data:
            if isinstance(part, FactoredRationalObject):
                new_factors = list((Counter(lcd)-Counter(part.denomenator)).elements())
                new_n, new_d = part.numerator + new_factors, lcd
                output.append(FactoredRationalObject(new_n, new_d))
            else:
                output.append(part)
        return output
        

    def find_lcd(self, expression_data):
        lcd = []
        for part in expression_data:
            if isinstance(part, FactoredRationalObject):
                lcd += list((Counter(part.denomenator)-Counter(lcd)).elements())
        return lcd

    def simp_negatives(self, expression_data):
        """
        Distributes negatives and turns subtraction signs into addition

        Returns expression_data without double/triple/quadruple negatives or subtraction signs
        """
        output =[]
        for index, part in enumerate(expression_data):
            if isinstance(part, RationalObject):
                
                if expression_data[index-1] == "-":
                    negative_numerator = "-" + part.numerator
                else:
                    negative_numerator = part.numerator

                non_neg_num, non_neg_denom = str(sympify(negative_numerator)), str(sympify(part.denomenator))
                output.append(RationalObject(non_neg_num, non_neg_denom))
            
            elif part == "-" and len(output) % 2 == 1:
                output.append("+")
                
            elif part != "-":
                output.append(part)
        
        return output

    def expand_numerator(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, FactoredRationalObject):
                numerator_sympy = sympify(part.get_n_str())
                expanded_numerator = numerator_sympy.expand()
                output.append(FactoredRationalObject([expanded_numerator], part.denomenator))
            else:
                output.append(part)
        return output

    def final_add(self, expression_data):
        output_numerator = []
        for part in expression_data:
            if isinstance(part, FactoredRationalObject):
                output_numerator.append(part.get_n_str())
                output_denomenator = part.denomenator
        numerator_sympy = sympify("+".join(output_numerator))
        final_numerator = simplify(numerator_sympy)
        return [FactoredRationalObject([final_numerator], output_denomenator)]


    def get_sympy_str(self, expression_data):
        output = []
        for part in expression_data:
            if isinstance(part, (RationalObject, FactoredRationalObject)):
                output.append(str(part))
            else:
                output.append(part)
        return sympify("".join(output), evaluate=False)


    def print_out(self, expression_data, message):
        sympy_str = self.get_sympy_str(expression_data)
        print(message)
        pretty_print(sympy_str)
        print("")
        print("")








class Expression(RationalBaseClass):
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
        """#"\s?(-|\+|\*|\s/\s)?\s?\(?(\(.+?\)|[0-9]*?)/(\(.+?\)|[0-9]*?)"
        #"\s?(-|\+|\*| / )?\s?(\(.+?\)|[0-9]*|.+?)/(\(.+?\)|[0-9]*)"
        #"\s?(-|\+|\*| / )?\s?(\(.+?\)|[0-9]*|.+?)/(\(.+?\)|[0-9]*|.+?)"
        #"\s?(-|\+|\*| / )?\s?\(?(\(.+?\)|[0-9]*|.+?)/(\(.+?\)|[0-9]*|.+?)\)?"
        #"\s?(\+|\*|/)?\s?\(?\(?(\(.+?\)|[0-9]*|.+?)/(\(.+?\)|[0-9]*|.+?)\)?\)?"  best
        self.expression_data = []
        broken_down = findall("\s?(-|\+|\*|/)?\s?\(?\(?\(?\(?(\(.+?\)|[0-9]*|.+?)/(\(.+?\)|[0-9]*|.+?)\)?\)?\)?", input_str) 
        for rational in broken_down:
            if rational[0]:
                self.expression_data.append(rational[0])
            rational_ob = RationalObject(rational[1], rational[2]) 
            self.expression_data.append(rational_ob)

        self.print_out(self.expression_data, "")
    
    def process_expression(self):
        """
        Checks operators in expression_data and directs it to other methods based on operator
        Negative sign always distributed first if present, no subtraction
        """
        no_neg_expression_data = self.simp_negatives(self.expression_data)
        if no_neg_expression_data != self.expression_data:
            self.print_out(no_neg_expression_data, "Simplify and distribute negatives")

        if len(no_neg_expression_data) <= 2:
            processed_expression_data = self.simp(no_neg_expression_data)
        
        if "/" in no_neg_expression_data:
            processed_expression_data = self.divide(no_neg_expression_data)
        
        if "*" in no_neg_expression_data:
            processed_expression_data = self.multiply(no_neg_expression_data)
        
        if "+" in no_neg_expression_data:
            processed_expression_data = add(no_neg_expression_data)
        
        final_expression_data = self.cancel_lc(processed_expression_data)
        if final_expression_data != processed_expression_data:
            self.print_out(final_expression_data, "completely simplify")


    def simp(self, input_expression_data):
        """
        Simplifies a rational expression - factors and cancels, then returns the new expression_data
        Built in a way that makes it reusable for other operator methods that also factor and cancel
        """
        
        factored_expression_data = self.factor_rationals(input_expression_data)
        self.print_out(factored_expression_data, "factor")
        canceled_expression_data = self.cancel_factors(factored_expression_data)
        self.print_out(canceled_expression_data, "cancel")
        
        return canceled_expression_data
        
    def add(self, input_expression_data):
        factored_expression_data = self.factor_rationals(input_expression_data, factor_numerator=False)
        self.print_out(factored_expression_data, "factor denomenator")
        #dont factor numerator and when applying lcd work it out using sympify and expand
        lcd_expression_data = self.apply_lcd(factored_expression_data)
        self.print_out(lcd_expression_data, "find and apply lcd")
        expanded_expression_data = self.expand_numerator(lcd_expression_data)
        self.print_out(expanded_expression_data, "")
        added_expression_data = self.final_add(expanded_expression_data)
        self.print_out(added_expression_data, "add numerators")
        print(added_expression_data)
        return added_expression_data

    def multiply(self, input_expression_data):
        """
        Multiples two rationals together - factors and cancels and multiplies, then returns new expression_data
        Calls simp() to factor and cancel
        """
        canceled_expression_data = self.simp(input_expression_data)
        muliplied_expression_data = self.multiply_factors(canceled_expression_data)
        self.print_out(muliplied_expression_data, "multiply numerator and denomenator")
        return canceled_expression_data

    def divide(self, input_expression_data):
        """
        Divides two rationals together - flip and factors and cancels and multiplies
        Calls multiply() to multiply after flipping and changing signs
        """
        divisor = input_expression_data[2]
        flipped_divisor = RationalObject(divisor.denomenator, divisor.numerator)
        flipped_expression_data = [input_expression_data[0]]+ ["*"] + [flipped_divisor]
        
        self.print_out(flipped_expression_data, "flip divisor and change sign")

        canceled_expression_data = self.multiply(flipped_expression_data)
        
        return canceled_expression_data


    @classmethod
    def from_latex(cls, latex_str):
        #raw_latex_str = r"{}".format(latex_str)
        latex_str = subsitute(r"\\left|\\right", "", latex_str)
        sympy_str = str(sympify(parse_latex(latex_str)))
        print(sympy_str)
        return cls(sympy_str)


class Equation(RationalBaseClass):
    def solve(self):
        pass

class PFD(RationalBaseClass):
    def check_improper(self):
        pass

class ComplexFractions(RationalBaseClass):
    pass
#r"\left(-\frac{x^2}{3x-6}\right)\cdot-\left(\frac{12}{6x}\right)"
test = {r" \frac{\left(n+2\right)}{10n^2+20n}":r"\frac{1}{10n}", r"\frac{\left(30n-24\right)}{54n^2}": r"\frac{\left(5n-4\right)}{9n^2}", r"\frac{81x}{18x^2+90}": r"\frac{9}{2x+10}", 
r"\frac{\left(x+40\right)}{2x^2+99x+760}": r"\frac{1}{2x+19}", r"\frac{\left(7n^2-36n-36\right)}{49n+42}\cdot\frac{\left(35n+42\right)}{30n+36}": r"\frac{\left(n-6\right)}{6}", 
r"\frac{\left(21n-49\right)}{7-3n}\cdot\frac{\left(5n^2+30n+25\right)}{35n+35}": r"-\left(n+5\right)", 
r"\frac{\left(8p^3-32p^2\right)}{5p^2+28p-49}\cdot\frac{\left(5p-7\right)}{8p^3-64p^2}": r"\frac{\left(p-4\right)}{\left(p+7\right)\left(p-8\right)}", 
r"\frac{\frac{\left(5x-40\right)}{25x+15}}{\frac{6x}{20x+12}}": r"\frac{2\left(x-8\right)}{3x}"}



test2 = {r"\frac{3}{x-1}+\frac{6x}{2x+3}" : r"\frac{\left(3\left(2x^2+3\right)\right)}{\left(x-1\right)\left(2x+3\right)}", r"\frac{7x}{x-5}-\frac{4}{5-x}": r"\frac{\left(7x+4\right)}{x-5}",
r"\frac{\left(x^2-12x+1\right)}{x+5}+\frac{\left(x^2-9\right)}{x-4}": ""}
if __name__ == "__main__": # "\left(-\frac{\left(x^2+4x-12\right)}{3x-6}\right)\cdot-\left(\frac{\left(4x+7x\right)}{6x}\right)"
    a = []
    for problem, answer in test.items():
        expression_ob = Expression.from_latex(problem)
        got_answer_data = expression_ob.process_expression()
        

        #actual_answer_ob = expression_ob.from_latex(answer)
        #actual_answer_ob.get_sympy_str(actual_answer_ob)