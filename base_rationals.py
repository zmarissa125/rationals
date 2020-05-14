from sympy import cancel, expand, factor, latex, pretty_print, simplify, sympify, factor_list

from re import sub as subsitute, findall, match
from collections import Counter


class RationalObject(object): # index
    def __init__(self, numerator, denomenator):
        if not denomenator:
            denomenator = "1"
        processed_numerator, processed_denomenator = self.balance_parenthesis(numerator), self.balance_parenthesis(denomenator)
        self.numerator = processed_numerator  #check for parenthesis here?
        self.denomenator = processed_denomenator
        
    def balance_parenthesis(self, n_or_d):
        
        n_or_d = str(n_or_d)

        eliminated_paren = list(subsitute(r"^\(\(?|\)$", "", n_or_d))
        balanced_paren = []

        counter = 0
        for char in eliminated_paren:
            if char == "(":
                counter += 1
            elif char == ")":
                counter -= 1
            if counter < 0:
                balanced_paren.insert(0, "(")
                counter += 1
            balanced_paren.append(char)

        if counter > 0:
            balanced_paren += [")"] * counter
    
        return "".join(balanced_paren)


    def __str__(self):
        processed_numerator = "({})".format(self.numerator)
        processed_denomenator = "({})".format(self.denomenator)
        if processed_denomenator == "(1)":
            return processed_numerator
        return "({} / {})".format(processed_numerator, processed_denomenator)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, RationalObject):
            if sympify(str(self)) == sympify(str(other)):
                return True
        else:
            if str(self) == str(other):
                return True
    def __mul__(self, other):
        if isinstance(other, RationalObject):
            n1, d1 = "({})".format(self.numerator), "({})".format(self.denomenator)
            n2, d2 = "({})".format(other.numerator), "({})".format(other.denomenator)
            new_n = simplify(sympify("{}*{}".format(n1,n2)))
            new_d = simplify(sympify("{}*{}".format(d1,d2)))
            return RationalObject(str(new_n), str(new_d))




class FactoredRationalObject(object):
    def __init__(self, numerator, denomenator):
        self.numerator = []
        self.denomenator = []
    
        for n in numerator:
            without_paren = subsitute(r"\(|\)", "", str(n))
            if n != 1 or len(numerator) == 1:
                self.numerator.append(n)
 
        for d in denomenator:
            without_paren = subsitute(r"\(|\)", "", str(d))
            if d != 1 or len(denomenator) == 1:
                self.denomenator.append(d)

        if not self.numerator:
            self.numerator.append(1)
        if not self.denomenator:
            self.denomenator.append(1)
        
  
    def get_lc(self):
        numerator_factors = factor_list(self.get_n_str())
        n_no_lc = self.no_powers(numerator_factors, include_lc = False)
        n_lc = int(numerator_factors[0])
        
        denomenator_factors = factor_list(self.get_d_str())
        d_no_lc = self.no_powers(denomenator_factors, include_lc = False)
        d_lc = int(denomenator_factors[0])

        return n_lc, n_no_lc, d_lc, d_no_lc
        
    
    def get_n_str(self):
        n = ["({})".format(individual_factor) for individual_factor in self.numerator]
        return "*".join(n)

    def get_d_str(self):
        d = ["({})".format(individual_factor) for individual_factor in self.denomenator]
        return "*".join(d)

    def __str__(self):
        n = self.get_n_str()
        d = self.get_d_str()
        n_string = "({})".format(n)
        d_string = "({})".format(d)
        
        if d_string == "((1))":
            return "({})".format(n_string)
            
        return "({} / {})".format(n_string, d_string)
    
    
    def __repr__(self):
        return str(self)


    def __mul__(self, other):
        if isinstance(other, FactoredRationalObject):
            n, d = other.numerator, other.denomenator
            return FactoredRationalObject(self.numerator + n, self.denomenator + d)

    def __add__(self, other):
        if isinstance(other, FactoredRationalObject):
            d = other.denomenator
            
            if d == self.denomenator:
                new_n = simplify(sympify("{} + {}".format(self.get_n_str(), other.get_n_str())))
                print(new_n)
                return FactoredRationalObject([new_n], self.denomenator)

    def __eq__(self, other):
        if isinstance(other, FactoredRationalObject):
            n1, n2 = Counter(self.numerator).elements, Counter(other.numerator).elements
            d1, d2 = Counter(self.denomenator).elements, Counter(other.denomenator).elements
            if n1 == n2 and d1 == d2:
                return True
        if str(self) == str(other):
            return True
    

    @staticmethod
    def no_powers(factor_list, include_lc = True): 
        if include_lc:
            unpacked_list = [factor_list[0]]
        else:
            unpacked_list =[]

        for f in factor_list[1]:
            unpacked_list += [f[0]] * f[1]
        return unpacked_list

    @classmethod
    def from_factored_str(cls, numerator, denomenator, factor_numerator):
        if factor_numerator:
            unpacked_numerator = cls.no_powers(factor_list(numerator))
        else:
            unpacked_numerator = [str(numerator.expand())]

        unpacked_denomenator = cls.no_powers(factor_list(denomenator))

        return cls(unpacked_numerator, unpacked_denomenator)










class ComplexRationalObject(object):
    """
    [expression data with RationalObjects]/[expression_data with RationalObjects]
    """
    def __init__(self, numerator, denomenator):
        self.numerator = [term for term in numerator if term != "(" and term != ")"]
        self.denomenator = [term for term in denomenator if term != "(" and term != ")"]

    def __str__(self):
        n_str = str(data_to_sympy_expression(self.numerator))
        d_str = str(data_to_sympy_expression(self.denomenator))
        return "({})/({})".format(n_str, d_str)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, ComplexRationalObject):
            if self.numerator == other.numerator and self.denomenator == other.denomenator:
                return True









def distribute_negatives(expression_data):
    """
    Distributes negatives and turns subtraction signs into addition

    Returns expression_data without double/triple/quadruple negatives or subtraction signs
    """
    output =[]
    for index, part in enumerate(expression_data):
        if isinstance(part, RationalObject):
            
            if expression_data[index-1] == "-":
                negative_numerator = "-({})".format(part.numerator)
            else:
                negative_numerator = part.numerator

            non_neg_num, non_neg_denom = str(sympify(negative_numerator)), str(sympify(part.denomenator))
            output.append(RationalObject(non_neg_num, non_neg_denom))
        
        elif part == "-" and len(output) % 2 == 1:
            output.append("+")
            
        elif part != "-":
            output.append(part)
    
    return output


def factor_rationals(expression_data, factor_numerator = True):
    output = []
    for part in expression_data: 
        
        if isinstance(part, RationalObject):
            factored_numerator, factored_denomenator = factor(part.numerator), factor(part.denomenator)
            output.append(FactoredRationalObject.from_factored_str(factored_numerator, factored_denomenator, factor_numerator))

        elif isinstance(part, FactoredRationalObject):
            factored_numerator, factored_denomenator = factor(part.get_n_str()), factor(part.get_d_str())
            output.append(FactoredRationalObject.from_factored_str(factored_numerator, factored_denomenator, factor_numerator))

        else:
            output.append(part)

    return output




def cancel_multiplication_factors(expression_data):
    output = []
    numerators, denomenators = get_all_nd(expression_data)
    for part in expression_data:
        
        if isinstance(part, FactoredRationalObject):
            canceled_n, denomenators = cancel_helper(part.numerator, denomenators)
            canceled_d, numerators = cancel_helper(part.denomenator, numerators)
            output.append(FactoredRationalObject(canceled_n, canceled_d))
        else:
            output.append(part)
    
    return output

def get_all_nd(expression_data):
    numerators = []
    denomenators = []
    for part in expression_data:
        if isinstance(part, FactoredRationalObject):
            numerators += part.numerator
            denomenators += part.denomenator
        
        elif isinstance(part, RationalObject):
            numerators.append(part.numerator)
            denomenators.append(part.denomenator)
   
    return numerators, denomenators
                
def cancel_helper(n_or_d, comparison_list):
    canceled_n_or_d = []
    for factor in n_or_d:
        if factor not in comparison_list:
            canceled_n_or_d.append(factor)
        else:
            comparison_list.remove(factor)
    return canceled_n_or_d, comparison_list








        
def simp_ints(expression_data):
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


def apply_lcd(expression_data, lcd, expression):
    output = []
    for part in expression_data:
        if isinstance(part, FactoredRationalObject):
            if expression:
                new_factors = list((Counter(lcd)-Counter(part.denomenator)).elements())
                new_n, new_d = part.numerator + new_factors, lcd
            else:
                new_n, new_d = part.numerator + lcd, part.denomenator
            
            output.append(FactoredRationalObject(new_n, new_d))
        else:
            output.append(part)
    return output


def find_lcd(expression_data):
    lcd = []
    for part in expression_data:
        if isinstance(part, FactoredRationalObject):
            lcd += list((Counter(part.denomenator)-Counter(lcd)).elements())

    return lcd



def expand_numerator(expression_data):
    output = []
    for part in expression_data:
        if isinstance(part, FactoredRationalObject):
            numerator_sympy = sympify(part.get_n_str())
            expanded_numerator = numerator_sympy.expand()
            output.append(FactoredRationalObject([expanded_numerator], part.denomenator))
        else:
            output.append(part)
    return output


def final_add(expression_data):  #fixxx
    for index, part in enumerate(expression_data):
        if index < len(expression_data)-1:
            if isinstance(part, FactoredRationalObject) and expression_data[index+1] == "+" and isinstance(expression_data[index+2], FactoredRationalObject):
                part = part + expression_data[index+2]

                expression_data[index], expression_data[index+1], expression_data[index+2] = None, None, part
        
    output = [part for part in expression_data if part]
    return output


def cancel_addition_factors(expression_data):
    output = []
    for part in expression_data:
        if isinstance(part, FactoredRationalObject):
            new_n = list((Counter(part.numerator)-Counter(part.denomenator)).elements())
            new_d = list((Counter(part.denomenator)-Counter(part.numerator)).elements())
            output.append(FactoredRationalObject(new_n, new_d))
        else:
            output.append(part)

    return output


def data_to_sympy_expression(expression_data):
    output = []
    for part in expression_data:
        if isinstance(part, (RationalObject, FactoredRationalObject)):
            output.append(str(part))
        else:
            output.append(part)
    return sympify("".join(output), evaluate=False)

