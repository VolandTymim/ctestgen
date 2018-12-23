from ctestgen.generator import *

example_program = Program('example_program')
example_program.add_include(Include('stdlib.h'))

max_define = Define('MAX(a,b)', '(a > b ? a : b)')
example_program.add_define(max_define)

example_enum = Enum(('N', 100), ('M', 10), 'G')
example_program.add_enum(example_enum)

global_const_a = ConstInt('a', 15)
example_program.add_global_variable(global_const_a)

main_function = Function('main', Int, Int('argc'), Pointer(Pointer(Char))('argv'))

var_b = Int('b')
var_max = Int('max')
var_ptr = Pointer(Int)('example_alloc_ptr')
main_body = CodeBlock(
    Assignment(VarDeclaration(var_b), 1),
    Assignment(var_max, max_define.process_macros(global_const_a, var_b)),
    Assignment(var_ptr, malloc(Mul(SizeOf(Int), example_enum[0], example_enum[1]))),
    free(var_ptr),
    Return(0)
)

main_function.set_body(main_body)
example_program.add_function(main_function)

print(example_program)
