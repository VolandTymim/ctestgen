import re
from typing import List


class Operator:
    def __init__(self, operator_definition, is_repeatable=False):
        self.operator_definition = operator_definition
        # counting format fields in operator definition
        self.arguments_count = len(re.findall(r'\{[^\}]*\}', operator_definition))
        self.is_repeatable = is_repeatable

    def generate_operator_code(self, *args):
        # if args and isinstance(args[0], Iterable) and not isinstance(args[0], str):
        if args and isinstance(args[0], List):
            args = args[0]
        if len(args) == self.arguments_count:
            return self.operator_definition.format(args=args)
        if self.is_repeatable and self.arguments_count == 2:
            # recursive call
            return self.operator_definition.format(args=(args[0], self.generate_operator_code(*args[1:])))
        assert False, 'Arguments count mismatch'

    def __call__(self, *args):
        return self.generate_operator_code(*args)


Assignment = Operator('{args[0]} = {args[1]}')

Add = Operator('{args[0]} + {args[1]}', True)
Sub = Operator('{args[0]} - {args[1]}', True)
Mul = Operator('{args[0]} * {args[1]}', True)
Div = Operator('{args[0]} / {args[1]}', True)
Modulo = Operator('{args[0]} % {args[1]}', True)

Increment = Operator('{args[0]}++')
IncrementPrefix = Operator('++{args[0]}')
Decrement = Operator('{args[0]}--')
DecrementPrefix = Operator('--{args[0]}')

IsEqual = Operator('{args[0]} == {args[1]}')
IsNotEqual = Operator('{args[0]} != {args[1]}')
IsGreater = Operator('{args[0]} > {args[1]}')
IsGreaterOrEqual = Operator('{args[0]} >= {args[1]}')
IsLess = Operator('{args[0]} < {args[1]}')
IsLessOrEqual = Operator('{args[0]} <= {args[1]}')

Not = Operator('!{args[0]}')
And = Operator('{args[0]} && {args[1]}', True)
Or = Operator('{args[0]} || {args[1]}', True)

BitNot = Operator('~{args[0]}')
BitAnd = Operator('{args[0]} & {args[1]}', True)
BitOr = Operator('{args[0]} | {args[1]}', True)
BitXor = Operator('{args[0]} ^ {args[1]}', True)
BitLeftShift = Operator('{args[0]} << {args[1]}', True)
BitRightShift = Operator('{args[0]} >> {args[1]}', True)

AddAssignment = Operator('{args[0]} += {args[1]}')
SubAssignment = Operator('{args[0]} -= {args[1]}')
MultAssignment = Operator('{args[0]} *= {args[1]}')
DivAssignment = Operator('{args[0]} /= {args[1]}')
ModuloAssignment = Operator('{args[0]} %= {args[1]}')
BitAndAssignment = Operator('{args[0]} &= {args[1]}')
BitOrAssignment = Operator('{args[0]} |= {args[1]}')
BitXorAssignment = Operator('{args[0]} ^= {args[1]}')
BitLeftShiftAssignment = Operator('{args[0]} <<= {args[1]}')
BitRightShiftAssignment = Operator('{args[0]} >>= {args[1]}')


class SubscriptOperator(Operator):
    def __init__(self):
        """Arguments count is dynamically changed value, there is no meaningful value for it"""
        super().__init__('[]')

    def __call__(self, *args):
        if args and isinstance(args[0], List):
            args = args[0]
        assert (len(args) > 1), \
            'Arguments count in call not match operator`s minimal arguments count'
        args[0].subscripts.append(args[1:])
        self.arguments_count = len(args)
        self.operator_definition = '{args[0]}'
        for i in range(1, len(args)):
            self.operator_definition += '[{args[' + str(i) + ']}]'
        return self.generate_operator_code(*args)


Subscript = SubscriptOperator()

Indirection = Operator('*{args[0]}')
AddressOf = Operator('&{args[0]}')
StructureReference = Operator('{args[0]}.{args[1]}', True)
StructureDereference = Operator('{args[0]}->{args[1]}', True)


class _CallOperator(Operator):
    def __init__(self):
        """Arguments count is dynamically changed value, there is no meaningful value for it"""
        super().__init__('()')

    def __call__(self, *args):
        if args and isinstance(args[0], List):
            args = args[0]
        assert (len(args) > 1), \
            'Arguments count in call not match operator`s minimal arguments count'
        self.arguments_count = len(args)
        self.operator_definition = '{args[0]}('
        for i in range(1, len(args)):
            if i != 1:
                self.operator_definition += ', '
            self.operator_definition += '{args[' + str(i) + ']}'
        self.operator_definition += ')'
        return self.generate_operator_code(*args)


Call = _CallOperator()

TernaryCondition = Operator('{args[0]} ? {args[1]} : {args[2]}')

Conversion = Operator('({args[0]}) {args[1]}')

SizeOf = Operator('sizeof({args[0]})')


class _VarDeclarationOperator(Operator):
    def __init__(self):
        super().__init__('{args[0]}')

    def __call__(self, var):
        return self.generate_operator_code(var.get_declaration())


VarDeclaration = _VarDeclarationOperator()

Return = Operator('return {args[0]}')
Break = Operator('break')
Continue = Operator('continue')
