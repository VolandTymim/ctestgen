from ctestgen.generator import *

var_a = Int('a')
var_b = Int('b')
example_block = CodeBlock(
    Assignment(VarDeclaration(var_a), 10),
    Assignment(VarDeclaration(var_b), 20),
    Assignment(var_a, Add(var_a, var_b))
)

print(example_block)

var_a = Float('a')
var_b = Float('b')
var_c = Float('c')
SumAndMul = Operator('({args[0]} + {args[1]}) * {args[2]}')
print(SumAndMul(var_a, var_b, var_c))

stdlib_include = (Include('stdlib.h'))
print(stdlib_include)

max_define = Define('MAX(a,b)', '(a > b ? a : b)')
var_b = Float('b')
var_c = Float('c')
print(max_define.get_declaration())
print(max_define(var_b, var_c))
print(max_define.process_macros(var_b, var_c))

dim0_template = LinearDimSubscriptTemplate(1, 0)
dim1_template = LinearDimSubscriptTemplate(0, 2)
dim2_template = LinearDimSubscriptTemplate(5, 7)
array_subscript_template = ArraySubscriptTemplate([dim0_template, dim1_template, dim2_template])
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (0, 2), (5, 7)])
iter_var0 = Int('i')
iter_var1 = Int('j')
iter_var2 = Int('k')
var_array1 = Array('A1', Int, 100, 200)
array_sizes_enum = Enum(('N', 10), ('M', 20))
var_array2 = Array('A2', Int, array_sizes_enum.constants)
print(array_subscript_template.generate_subscript(var_array1, [iter_var0, iter_var1, iter_var2]))
print(array_subscript_template.generate_subscript(var_array2, [iter_var0, iter_var1, iter_var2]))

array_sizes_enum = Enum(('N', 10), ('M', 20))
var_array = Array('A', Int, array_sizes_enum.constants)
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (5, 7)])

iter_var0 = Int('i')
iter_var1 = Int('j')

for0_init = Assignment(VarDeclaration(iter_var0), 0)
for0_continue_condition = IsLess(iter_var0, array_sizes_enum[0])
for0_step = Increment(iter_var0)
for0_loop = For(for0_init, for0_continue_condition, for0_step)

for1_init = Assignment(VarDeclaration(iter_var1), 0)
for1_continue_condition = IsLess(iter_var1, array_sizes_enum[1])
for1_step = Increment(iter_var1)
for1_body = CodeBlock(
    Assignment(array_subscript_template.generate_subscript(var_array, [iter_var0, iter_var1]), 15)
)

for1_loop = For(for1_init, for1_continue_condition, for1_step, for1_body)

for0_body = CodeBlock(for1_loop)
for0_loop.set_body(for0_body)
print(for0_loop)

array_sizes_enum = Enum(('N', 10), ('M', 20))
var_array = Array('A', Int, array_sizes_enum.constants)
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (5, 7)])

print(pass_array(var_array, array_subscript_template, assignment_source=15))

array_sizes_enum = Enum(('N', 10), ('M', 20), ('K', 30))
var_array = Array('A', Double, array_sizes_enum.constants)
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (5, 7), (0, 2)])
assignment_var = Double('s')
print(pass_array(var_array,
                 array_subscript_template,
                 assignment_source=IncrementPrefix(assignment_var)))

array_sizes_enum = Enum(('N', 10), ('M', 20), ('K', 30), ('O', 40))
var_array = Array('A', Double, array_sizes_enum.constants)
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (5, 7), (0, 2), (2, 2)])
assignment_var = Double('s')
print(pass_array(var_array,
                 array_subscript_template,
                 assignment_source=IncrementPrefix(assignment_var),
                 iter_var_type=SizeT))

dims_count = 4
names = generate_dim_sizes_names(dims_count)
enum_constants = [(names[i], (i + 1) * 100) for i in range(dims_count)]
enum_example = Enum(enum_constants)
print(enum_example.get_declaration())
