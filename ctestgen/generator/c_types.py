from typing import Tuple
from typing import List
from ctestgen.generator import Define
from ctestgen.generator.style_parametres import indent_size, indent_char


class EnumConstant:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def get_declaration(self):
        enum_constant_code = self.name
        if self.value:
            enum_constant_code += ' = ' + str(self.value)
        return enum_constant_code

    def __str__(self):
        return self.name


class Enum:
    def __init__(self, *constants, name=None):
        """ Usage like Enum(('K', 7), ('M', 8), 'G')"""
        if isinstance(constants[0], List):
            constants = constants[0]
        self.constants = [EnumConstant(c[0], c[1]) if isinstance(c, Tuple) else EnumConstant(c) for c in constants]
        self.name = name

    def _get_title(self):
        return 'enum ' + self.name if self.name else 'enum'

    def get_declaration(self):
        enum_code = self._get_title() + ' {'
        add_comma = False
        for constant in self.constants:
            if add_comma:
                enum_code += ',\n' + indent_size * indent_char
            else:
                enum_code += '\n' + indent_size * indent_char
                add_comma = True

            enum_code += constant.get_declaration()

        enum_code += '\n};\n\n'
        return enum_code

    def __str__(self):
        return self._get_title()

    def __getitem__(self, item):
        return self.constants[item]

    def __iter__(self):
        return self.constants.__iter__()


class Type:
    def __init__(self, typename):
        self.typename = typename

    def get_var_declaration(self, var_name):
        return self.typename + ' ' + var_name

    def __call__(self, name):
        return Var(name, self)

    def __str__(self):
        return self.typename


Char = Type('char')
Int = Type('int')
UInt = Type('unsigned int')
Long = Type('long')
SizeT = Type('size_t')
Float = Type('float')
Double = Type('double')
Void = Type('void')
Bool = Type('bool')


class Pointer(Type):
    def __init__(self, inner_type: Type):
        super().__init__(str(inner_type) + '*')
        self.inner_type = inner_type


class ConstType(Type):
    def __init__(self, inner_type: Type):
        super().__init__('const ' + str(inner_type))
        self.inner_type = inner_type

    def __call__(self, name, init_value=None):
        return ConstVar(name, self.inner_type, init_value)


ConstChar = ConstType(Char)
ConstInt = ConstType(Int)
ConstUInt = ConstType(UInt)
ConstLong = ConstType(Long)
ConstSizeT = ConstType(SizeT)
ConstFloat = ConstType(Float)
ConstDouble = ConstType(Double)
ConstVoid = ConstType(Void)
ConstBool = ConstType(Bool)


class ArrayType(Type):
    def __init__(self, base_type: Type, *dimension_sizes):
        super().__init__(str(base_type))
        if isinstance(dimension_sizes[0], List):
            dimension_sizes = dimension_sizes[0]
        self.dimension_sizes = dimension_sizes
        self.base_type = base_type

    def get_var_declaration(self, var_name):
        var_declaration = self.typename + ' ' + var_name
        for dim_size in self.dimension_sizes:
            var_declaration += '['
            if dim_size:
                if isinstance(dim_size, Var):
                    var_declaration += dim_size.name
                elif isinstance(dim_size, EnumConstant):
                    var_declaration += dim_size.name
                elif isinstance(dim_size, Define):
                    var_declaration += dim_size.macro_title
                else:
                    var_declaration += str(dim_size)
            var_declaration += ']'
        return var_declaration


class ArrayTypeC99(ArrayType):
    def get_var_declaration(self, var_name):
        var_declaration = self.typename + \
                          ' (*' + var_name + ')'
        for i in range(1, len(self.dimension_sizes)):
            dim_size = self.dimension_sizes[i]
            var_declaration += '['
            if dim_size:
                if isinstance(dim_size, Var):
                    var_declaration += dim_size.name
                elif isinstance(dim_size, EnumConstant):
                    var_declaration += dim_size.name
                elif isinstance(dim_size, Define):
                    var_declaration += dim_size.macro_title
            var_declaration += ']'
        return var_declaration


class Var:
    def __init__(self, name, var_type: Type):
        self.name = name
        self.var_type = var_type

    def get_declaration(self):
        return self.var_type.get_var_declaration(self.name)

    def __str__(self):
        return self.name


class ConstVar(Var):
    def __init__(self, name, base_type: Type, init_value=None):
        super().__init__(name, ConstType(base_type))
        self.init_value = init_value

    def get_declaration(self):
        declaration_code = self.var_type.get_var_declaration(self.name)
        if self.init_value:
            declaration_code += ' = ' + str(self.init_value)
        return declaration_code


class Array(Var):
    def __init__(self, name, base_type, *dim_sizes):
        super().__init__(name, ArrayType(base_type, *dim_sizes))
        self.subscripts = []
        self.subscript_templates = []


class ArrayC99(Var):
    def __init__(self, name, base_type, *dim_sizes):
        super().__init__(name, ArrayTypeC99(base_type, *dim_sizes))
        self.subscripts = []
        self.subscript_templates = []
