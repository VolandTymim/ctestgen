from abc import ABCMeta, abstractmethod
from ctestgen.generator import Add, Mul, Subscript


class DimSubscriptTemplate(metaclass=ABCMeta):
    @abstractmethod
    def generate_subscript(self, iter_var):
        pass

    @abstractmethod
    def get_coefficients(self):
        pass

    @abstractmethod
    def get_str_coefficients(self):
        pass

    def __str__(self):
        return str(self.get_coefficients())


class LinearDimSubscriptTemplate:
    """Template for generating subscript expression of form a*i + b"""

    def __init__(self, multiply_coefficient=0, add_coefficient=0):
        self.multiply_coefficient = multiply_coefficient
        self.add_coefficient = add_coefficient

    def generate_subscript(self, iter_var):
        if self.add_coefficient:
            if self.multiply_coefficient:
                return Add(Mul(iter_var, self.multiply_coefficient), self.add_coefficient)
            else:
                return str(self.add_coefficient)
        else:
            if self.multiply_coefficient:
                return Mul(iter_var, self.multiply_coefficient)
            else:
                return '0'

    def get_coefficients(self):
        return self.multiply_coefficient, self.add_coefficient

    def get_str_coefficients(self):
        return str(self.multiply_coefficient), str(self.add_coefficient)

    def __str__(self):
        return 'Mul coefficient: ' + str(self.multiply_coefficient) + \
               ' add coefficient: ' + str(self.add_coefficient)


class ArraySubscriptTemplate:
    def __init__(self, dim_templates):
        self.dim_templates = dim_templates

    def generate_subscript(self, array, iter_vars):
        assert len(self.dim_templates) == len(iter_vars), \
            'Dimensions count and given iterative variables count mismatch.' + str(self.dim_templates) + ' ' + str(iter_vars)
        array.subscript_templates.append(self)
        subscript_arguments = [array] + [self.dim_templates[i].generate_subscript(iter_vars[i])
                                         for i in range(len(self.dim_templates))]
        return Subscript(subscript_arguments)

    def get_coefficients(self):
        return [template.get_coefficients() for template in self.dim_templates]

    def get_str_coefficients(self):
        return [template.get_str_coefficients() for template in self.dim_templates]


class ArrayLinearSubscriptTemplate(ArraySubscriptTemplate):
    def __init__(self, args):
        """ArrayLinearSubscriptTemplate((1,3), (5,7), (9,11))"""
        super().__init__([LinearDimSubscriptTemplate(coefficients[0], coefficients[1]) for coefficients in args])
