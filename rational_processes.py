from sympy import factor, sympify, latex, factor_list
from sympy.parsing.latex import parse_latex
from re import sub as subsitute, findall, match
from collections import Counter
class ExpressionData(object):
    def __init__(self, list_data):
        pass

class RationalObject(object): # index
    def __init__(self, numerator, denomenator):
        processed_numerator = subsitute(r"\(|\)", "", numerator)
        processed_denomenator = subsitute(r"\(|\)", "", denomenator)
        self.numerator = processed_numerator  #check for parenthesis here?
        self.denomenator = processed_denomenator

    def __str__(self):
        processed_numerator = "({})".format(self.numerator)
        processed_denomenator = "({})".format(self.denomenator)
        return "({} / {})".format(processed_numerator, processed_denomenator)

    def __repr__(self):
        return str(self)

class FactoredRationalObject(object):
    def __init__(self, numerator, denomenator):
        processed_numerator = [subsitute(r"\(|\)", "", str(n)) for n in numerator]
        processed_denomenator = [subsitute(r"\(|\)", "", str(d)) for d in denomenator]
        
        self.numerator = processed_numerator
        self.denomenator = processed_denomenator
        

    def get_lc(self, n_or_d):
        factor_lc = 1
        no_lc = []
        print("--dwj")
        print(n_or_d)
        for indv_factor in n_or_d:
            new_lc = match("^[0-9]*$", indv_factor)
            if new_lc:
                factor_lc *= int(new_lc[0])
            else:
                no_lc.append(indv_factor)
                
        if factor_lc != 1:
            return factor_lc, no_lc
        
        return None, None


    def index_factors(self, index):
        return [Factor(f, index) for f in self.numerator], [Factor(f, index) for f in self.denomenator]

    @staticmethod
    def no_powers(factor_list): 
        unpacked_list = [factor_list[0]]

        factor_tuples = factor_list[1]
        for f in factor_tuples:
            unpacked_list += [f[0]] * f[1]
        
        return unpacked_list
    
    @classmethod
    def from_factored_str(cls, numerator, denomenator):
        unpacked_numerator = cls.no_powers(factor_list(numerator))
        unpacked_denomenator = cls.no_powers(factor_list(denomenator))

        return cls(unpacked_numerator, unpacked_denomenator)

    def __str__(self):
        n = ["({})".format(individual_factor) for individual_factor in self.numerator]
        d = ["({})".format(individual_factor) for individual_factor in self.denomenator]
        n_string = "({})".format("*".join(n))
        d_string = "({})".format("*".join(d))
        
        if d_string == "((1))":
            return "({})".format(n_string)
            
        return "({} / {})".format(n_string, d_string)

    def __repr__(self):
        return str(self)

class Factor(object):
    def __init__(self, info, index):
        self.info = info
        self.index = index

    def __eq__(self, other_instance):
        if self.info == other_instance.info:
            return True

    def __hash__(self):
        return hash(self.info)

    def __repr__(self):
        return str(self.info)