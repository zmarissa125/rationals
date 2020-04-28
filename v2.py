from sympy import factor, pretty_print, sympify, latex
from sympy.parsing.latex import parse_latex
from re import sub as subsitute, findall
from collections import Counter
from rational_processes import RationalObject, FactoredRationalObject, Factor

class RationalBaseClass(object): #Still be in class??
    """
    Performs all basic functions necessary to solve rational functions
    """
    def get_nd_factors(self, expression_data, index_factors = False):
        """
        Returns two lists: one list of all factors in the numerators of an expression, and one list for denomenators
        Can have list of factors as Index Objects (used for canceling)
        """
        denomenator_factors, numerator_factors = [], []
        
        for index, part in enumerate(expression_data):
            
            if isinstance(part, FactoredRationalObject):
                
                if index_factors:
                    n, d = part.index_factors(index)
                
                else:
                    n,d = part.numerator, part.denomenator
                
                numerator_factors += n
                denomenator_factors += d
        
        return numerator_factors, denomenator_factors

    def cancel_helper(self, factor_list, index):
        canceled_out = [single_factor for single_factor in factor_list if single_factor.index == index]
        
        if not canceled_out:
            canceled_out.append(1)
        
        return canceled_out

    def cancel_factors(self, expression_data): #maybe use sympy built in??
        numerator_factors, denomenator_factors = self.get_nd_factors(expression_data, index_factors= True)
        
        canceled_numerator = list((Counter(numerator_factors)-Counter(denomenator_factors)).elements())
        canceled_denomenator = list((Counter(denomenator_factors)-Counter(numerator_factors)).elements()) 
        
        output_expression_data = expression_data[:]
        for index, part  in enumerate(output_expression_data):
            
            if isinstance(part, FactoredRationalObject):
                n, d = self.cancel_helper(canceled_numerator, index), self.cancel_helper(canceled_denomenator, index)
                output_expression_data[index] = FactoredRationalObject(n,d)
        
        return output_expression_data


    def multiply_factors(self,expression_data):
        numerator_factors, denomenator_factors = self.get_nd_factors(expression_data)
        return [FactoredRationalObject(numerator_factors, denomenator_factors)]

    def factor_rational(self, rational_ob):
        factored_numerator, factored_denomenator = factor(rational_ob.numerator), factor(rational_ob.denomenator)
        return FactoredRationalObject.from_factored_str(factored_numerator, factored_denomenator)

    def gcd(self, factored_rational_ob):
        print(factored_rational_ob)
        numerator_lc, numerator_no_lc = factored_rational_ob.get_lc(factored_rational_ob.numerator)
        denomenator_lc, denomenator_no_lc = factored_rational_ob.get_lc(factored_rational_ob.denomenator)
        print(numerator_no_lc)
        if numerator_lc and denomenator_lc:
            a = int(numerator_lc)
            b = int(denomenator_lc)
            while b:
                a, b = b, a%b
            return FactoredRationalObject([int(numerator_lc/a)] + numerator_no_lc, [int(denomenator_lc/a)] + denomenator_no_lc)

        return factored_rational_ob

    def lcd(self):
        pass
        
    """
    def process_negative(self, expression_data):
        output_expression_data = []
        skip = 0
        for index, part in enumerate(expression_data):
            skip -= 1
            if part == "-":
                skip = 2
                next_rational = expression_data[index + 1]
                new_numerator = str(sympify(part + "(" + next_rational.numerator + ")" ))

                new_rational = RationalObject(new_numerator, next_rational.denomenator)

                if isinstance(expression_data[index - 1], RationalObject) and index != 0:
                    output_expression_data += ["+", new_rational]
                else:
                    output_expression_data.append(new_rational)
            elif skip <= 0:
                ouput_expression_data.append(part)
        return output_expression_data"""

                
                
    
    def print_out(self, expression_data, message):
        output = []
        for part in expression_data:
            if isinstance(part, (RationalObject, FactoredRationalObject)):
                output.append(str(part))
            else:
                output.append(part)
        print(message)
        pretty_print(sympify("".join(output), evaluate= False))
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
        self.expression_data = []
        broken_down = findall("\s?(-|\+|\*| / )?\s?\(?(\(.+?\)|[0-9]*|.+?)/(\(.+?\)|[0-9]*|.+?)\)?", input_str) 
        for rational in broken_down:
            if rational[0]:
                self.expression_data.append(rational[0])
            rational_ob = RationalObject(rational[1], rational[2]) 
            self.expression_data.append(rational_ob)
        print(self.expression_data)
        self.print_out(self.expression_data, "")
    
    def process_expression(self):
        """
        Checks operators in expression_data and directs it to other methods based on operator
        Negative sign always distributed first if present, no subtraction
        """
        if "-" in self.expression_data:
            self.expression_data = self.process_negative(self.expression_data)
            self.print_out(self.expression_data, "cancel negatives")   
        
        if len(self.expression_data) <= 2:
            return self.simp(self.expression_data)
        
        if "/" in self.expression_data:
            return self.divide(self.expression_data)
        
        if "*" in self.expression_data:
            return self.multiply(self.expression_data)
        
        if "+" in self.expression_data:
            return self.add(self.expression_data)

    def simp(self, input_expression_data):
        """
        Simplifies a rational expression - factors and cancels, then returns the new expression_data
        Built in a way that makes it reusable for other operator methods that also factor and cancel
        """
        factored_expression_data = []
        
        for part in input_expression_data:
            if isinstance(part, RationalObject):  #FIX!!!!
                new_part = self.factor_rational(part)
                factored_expression_data.append(new_part)
            else:
                factored_expression_data.append(part)

        self.print_out(factored_expression_data, "factor")
        canceled_expression_data = self.cancel_factors(factored_expression_data)
        self.print_out(canceled_expression_data, "cancel")
        print(canceled_expression_data)
        new_ob = self.gcd(canceled_expression_data[0]) # FIX
        self.print_out([new_ob], "yeet")
    

        return [new_ob]
        
    def add(self, input_expression_data):
        #Factor
        #Count each in a dictionary
        #Fill in and multiply so lcd
        pass


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
if __name__ == "__main__": # "\left(-\frac{\left(x^2+4x-12\right)}{3x-6}\right)\cdot-\left(\frac{\left(4x+7x\right)}{6x}\right)"
    a = []
    for problem, answer in test.items():
        expression_ob = Expression.from_latex(problem)
        recieved_answer = expression_ob.process_expression()
        
        
        answer_data = Expression.from_latex(answer)
        
        if recieved_answer != answer_data.expression_data:
            a.append((recieved_answer, answer_data.expression_data))
            print("ERROR")
            print(recieved_answer, answer_data.expression_data)
            print("")
            print("")
            print("______________________________________________________")
        else:
            print("Yess")

    