from sympy import factor, sympify, latex, factor_list, expand
from sympy.parsing.latex import parse_latex
from re import sub as subsitute, findall, match
from collections import Counter
class ExpressionData(object):
    def __init__(self, list_data):
        pass

class RationalObject(object): # index
    def __init__(self, numerator, denomenator):
        processed_numerator, processed_denomenator = self.balance_parenthesis(numerator), self.balance_parenthesis(denomenator)
        self.numerator = processed_numerator  #check for parenthesis here?
        self.denomenator = processed_denomenator

    def balance_parenthesis(self, n_or_d):
        
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
        return "({} / {})".format(processed_numerator, processed_denomenator)

    def __repr__(self):
        return str(self)

    def __eq__(self, other_instance):
        if str(self) == str(other_instance):
            return True






class FactoredRationalObject(object):
    def __init__(self, numerator, denomenator):
        self.numerator = []
        self.denomenator = []
        
        for n in numerator:
            without_paren = subsitute(r"\(|\)", "", str(n))
            if n != 1 or len(without_paren) < 2:
                self.numerator.append(n)
        
        for d in denomenator:
            without_paren = subsitute(r"\(|\)", "", str(d))
            if d != 1 or len(without_paren) < 2:
                self.denomenator.append(d)

        
        
#make all factor_list so easy lc??
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

    def __eq__(self, other_instance):
        if str(self) == str(other_instance):
            return True