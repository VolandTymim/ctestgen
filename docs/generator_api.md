# Generator API

## Overview

Root of **ctestgen** AST representation is `ctestgen.generator.Program` class. 
Program designed as a container for macros, enums, global variables and functions. 
Structures are currently not supported.

Basis of program code is `ctestgen.generator.CodeBlock` that representing C compound statement.
`CodeBlock` serves as a body for functions and control structures.

Additionally API contains some **utils** for faster code description.


## Program structure elements

### Program

`ctestgen.generator.Program` is root of AST representation, container for macros, enums, global variables and functions.

```python
from ctestgen.generator import Program
program = Program('example_program')
```

Class methods:

| Method | Description |
|:---: | :---:|
| `__str__()` | Text representation of program|
| `set_name(name)` | Change program name |
| `add_include(include)` | Add include macro definition to program |
| `add_define(define)` | Add define macro definition to program |
| `add_enum(self, enum)` | Add enum definition to program|
| `add_global_variable` | Add global variable definition to program |
| `add_function` | Add function definition to program |
| `write_to_file(output_dir)` | Write program to file <program name>.c in defined dir|

Example:

```python
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
```

Output:
```c
#include <stdlib.h>

#define MAX(a,b) (a > b ? a : b)

enum {
  N = 100,
  M = 10,
  G
};


const int a = 15;

int main(int argc, char** argv) {
  int b = 1;
  max = (a > b ? a : b);
  example_alloc_ptr = malloc(sizeof(int) * N * M);
  free(example_alloc_ptr);
  return 0;
}
```

### CodeBlock

Class `ctestgen.generator.CodeBlock` represents C compound statement.
```c
{
    <statement1>
    ...
    <statementn>
}
```

`CodeBlock` serves as a body for functions and control structures.
Class object creation takes list of statements for block.

Example:

```python
var_a = Int('a')
var_b = Int('b')
example_block = CodeBlock(
    Assignment(VarDeclaration(var_a), 10),
    Assignment(VarDeclaration(var_b), 20),
    Assignment(var_a, Add(var_a, var_b))
)
```
Output:
```c
{
    int a = 10;
    int b = 20;
    a = a + b;
}
```

### Function

Represents C function.

Example:
```python
arguments_count = 4
sum_arguments = [Int('num_' + str(arg_idx)) for arg_idx in range(arguments_count)]
sum_function = Function('sum_' + str(arguments_count) + '_nums', Int, sum_arguments)
sum_result = Int('sum')
sum_body = CodeBlock(
    Assignment(sum_result.get_declaration(), Add(sum_arguments)),
    Return(sum_result)
)
sum_function.set_body(sum_body)
print(sum_function.get_declaration())
```
Output:
```c
int sum_4_nums(int num_0, int num_1, int num_2, int num_3) {
  int sum = num_0 + num_1 + num_2 + num_3;
  return sum;
}
```

## Types system

Class `ctestgen.generator.Type` represents variable type. 
Concrete types as `Int`, `Float`, etc is objects of `Type`.

Class `ctestgen.generator.Var` represents variable.

`Type` is callable, it returns new `Var` object with corresponding var type.

```python
var_a = Int('a')
print(VarDeclaration(var_a))
```
Output:
```c 
int a
``` 
Code `Int('a')` equals to `Var('a', Int)`, choose what you like.

`ctestgen.generator.Pointer` is subclass of `Type`, and pointer variables 
created in a slightly different way.

```python
var_ptr1 = Pointer(Int)('ptr1')
var_ptr2 = Pointer(Pointer(Int))('ptr2')
var_ptr3 = Pointer(Pointer(Void))('ptr3')
print(VarDeclaration(var_ptr1))
print(VarDeclaration(var_ptr2))
print(VarDeclaration(var_ptr3))
```
Output:
```c 
int* ptr1
int** ptr2
void** ptr3
```

Array variable creation:
```python
var_array1 = Array('A1', Int, 100, 200, 300)
array_sizes_enum = Enum(('N', 100), ('M', 200))
var_array2 = Array('A2', Int, array_sizes_enum.constants)
print(VarDeclaration(var_array1))
print(VarDeclaration(var_array2)
```
Output:
```c
int A1[100][200][300]
int A1[N][M]
```

Code `Array('A1', Int, 100, 200, 300)` equals to `Array('A1', Int, [100, 200, 300])`.

Defined types:

| Lib type | C type |
|:---: | :---:|
| Char | char|
| Int | int|
| UInt | unsigned int|
| Long | long|
| SizeT | size_t|
| Float | float|
| Double | double|
| Void | void|
| Bool |  bool|
| ConstChar | const char|
| ConstInt | const int|
| ConstUInt | const unsigned int|
| ConstLong | const long|
| ConstSizeT | const size_t|
| ConstFloat | const float|
| ConstDouble | const double|
| ConstVoid | const void|
| ConstBool | const bool|
| Array | C array like int A\[N]|
| ArrayC99 | C99 array like int (*A)\[N]|

You can easily define new types:
```python
Int64 = Type('int64_t')
```


## Operators

Class `ctestgen.generator.Operator` represents C operator.
Concrete operators as `Assignment`, `Mul`, etc is objects of `Operator`.

`Operator` is callable, it returns text representation of operator call.
```python
var_a = Float('a')
var_b = Float('b')
var_c = Float('c')
print(Mul(var_a, var_b, var_c))
```
Output:
```c
a * b * c
```

Defined operators:

| Lib operator | C operator |
|:---: | :---:|
| Assignment | arg0 = arg1 |
| Add | arg0 + arg1 | 
| Sub | arg0 - arg1 | 
| Mul | arg0 * arg1 | 
| Div | arg0 / arg1 | 
| Modulo | arg0 % arg1 | 
| Increment | arg++ |
| IncrementPrefix | ++arg |
| Decrement | arg-- |
| DecrementPrefix | --arg |
| IsEqual | arg0 == arg1 |
| IsNotEqual | arg0 != arg1 |
| IsGreater | arg0 > arg1 |
| IsGreaterOrEqual | arg0 >= arg1 |
| IsLess | arg0 < arg1 |
| IsLessOrEqual | arg0 <= arg1 |
| Not | !arg |
| And | arg0 && arg1 |
| Or | arg0 &#124;&#124; arg1 |
| BitNot | ~arg0 |
| BitAnd | arg0 & arg1 |
| BitOr | arg0 &#124; arg1 |
| BitXor | arg0 ^ arg1 |
| BitLeftShift | arg0 << arg1 |
| BitRightShift | arg0 >> arg1 |
| AddAssignment | arg0 += arg1 |
| SubAssignment | arg0 -= arg1 |
| MultAssignment | arg0 *= arg1 |
| DivAssignment | arg0 /= arg1 |
| ModuloAssignment | arg0 %= arg1 |
| BitAndAssignment | arg0 &= arg1 |
| BitOrAssignment | arg0 &#124;= arg1 |
| BitXorAssignment | arg0 ^= arg1 |
| BitLeftShiftAssignment | arg0 <<= arg1 |
| BitRightShiftAssignment | arg0 >>= arg1 |
| Subscript | \[ arg0 \] |
| Indirection | *arg0 |
| AddressOf | &arg0 |
| StructureReference | arg0.arg1 |
| StructureDereference | arg0->arg1 |
| Call | \( \) |
| TernaryCondition | arg0 ? arg1 : arg2 |
| Conversion | (arg0) arg1 |
| SizeOf | sizeof(arg0) | 
| Return | return arg0 |
| Break | break |
| Continue | continue |

You can easily define new `Operator`:
```python
AddAndMul = Operator('({args[0]} + {args[1]}) * {args[2]}')
var_a = Float('a')
var_b = Float('b')
var_c = Float('c')
print(SumAndMul(var_a, var_b, var_c))
```
Output:
```c
(a + b) * c
```

## Macros

Currently only `Include` and `Define` macros implemented.

Example usage:
```python
max_define = Define('MAX(a,b)', '(a > b ? a : b)')
var_b = Float('b')
var_c = Float('c')
print(max_define.get_declaration())
print(max_define(var_b, var_c))
print(max_define.process_macros(var_b, var_c))
```
Output:
```c
#include <stdlib.h>

#define MAX(a,b) (a > b ? a : b)

MAX(b, c)
(b > c ? b : c)
```

## Control structures

### If

Class `ctestgen.generator.If` represents C `if` control statement.
Example:
```python
var_a = Int('a')
condition = IsGreaterOrEqual(var_a, 0)
true_body = CodeBlock(
    Assignment(var_a, 100)
)
false_body = CodeBlock(
    Assignment(var_a, -100)
)
if_example = If(condition, true_body, false_body)
print(if_example)
```
Output:
```c
if (a >= 0) {
  a = 100;
} else {
  a = -100;
}
```
### For

Class `ctestgen.generator.For` represents C `For` loop.
Example:
```python
var_a = Int('a')
var_i = SizeT('i')
init = Assignment(VarDeclaration(var_i), 0)
continue_condition = IsLess(var_i, 100)
step = Increment(var_i)
body = CodeBlock(
    AddAssignment(var_a, 2)
)
for_example = For(init, continue_condition, step, body)
print(for_example)
```
Output:
```c
for (size_t i = 0; i < 100; i++) {
  a += 2;
}
```
### While

Class `ctestgen.generator.While` represents C `while` loop.
Example:
```python
var_a = Int('a')
continue_condition = IsLess(var_a, 33)
body = CodeBlock(
    AddAssignment(var_a, 15)
)
while_example = While(continue_condition, body)
print(while_example)
```
Output:
```c
while (a < 33) {
  a += 15;
}
```
## Utils

### Templates

#### ArraySubscriptTemplate

Class `ctestgen.generator.ArraySubscriptTemplate` designed to 
define array subscript expressions in loops. It contains templates for every 
array dimension subscript expression, that defined in class object creation.

Dimension subscript expression is are defined by objects of subclasses 
of abstract class `ctestgen.generator.DimSubscriptTemplate`

Currently implemented `LinearDimSubscriptTemplate` - template for generating 
expressions of form `a * iter_var + b`.

Example:
```python
dim0_template = LinearDimSubscriptTemplate(1, 0)
dim1_template = LinearDimSubscriptTemplate(0, 2)
dim2_template = LinearDimSubscriptTemplate(5, 7)
array_subscript_template = ArraySubscriptTemplate([dim0_template, dim1_template, dim2_template])
iter_var0 = Int('i')
iter_var1 = Int('j')
iter_var2 = Int('k')
var_array1 = Array('A1', Int, 100, 200, 300)
array_sizes_enum = Enum(('N', 10), ('M', 20), ('K', 30))
var_array2 = Array('A2', Int, array_sizes_enum.constants)
print(array_subscript_template.generate_subscript(var_array1, [iter_var0, iter_var1, iter_var2]))
print(array_subscript_template.generate_subscript(var_array2, [iter_var0, iter_var1, iter_var2]))
```
Output:
```c
A1[i * 1][2][k * 5 + 7]
A2[i * 1][2][k * 5 + 7]
```
API contains shorter form for code:
```python
dim0_template = LinearDimSubscriptTemplate(1, 0)
dim1_template = LinearDimSubscriptTemplate(0, 2)
dim2_template = LinearDimSubscriptTemplate(5, 7)
array_subscript_template = ArraySubscriptTemplate([dim0_template, dim1_template, dim2_template])
```
This code equals to:
```python
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (0, 2), (5, 7)])
```

Example of usage in `For` loop.
Example:
```python
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
```
Output:
```c
for (int i = 0; i < N; i++) {
  for (int j = 0; j < M; j++) {
    A[i * 1][j * 5 + 7] = 15;
  }
}
```

To simplify this, API contains function to array passing.

#### Array passing

Function `ctestgen.generator.pass_array` designed to simplify arrays passing.

Simplify the previous example:
```python
array_sizes_enum = Enum(('N', 10), ('M', 20))
var_array = Array('A', Int, array_sizes_enum.constants)
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (5, 7)])

print(pass_array(var_array, array_subscript_template, assignment_source=15))
```
Output:
```c
for (int i0 = 0; i0 < N; i0++) {
  for (int i1 = 0; i1 < M; i1++) {
    A[i0 * 1][i1 * 5 + 7] = 15;
  }
}

```

More examples:
```python
array_sizes_enum = Enum(('N', 10), ('M', 20), ('K', 30))
var_array = Array('A', Double, array_sizes_enum.constants)
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (5, 7), (0, 2)])
assignment_var = Double('s')
print(pass_array(var_array,
                 array_subscript_template,
                 assignment_source=IncrementPrefix(assignment_var)))
```
Output:
```c
for (int i0 = 0; i0 < N; i0++) {
  for (int i1 = 0; i1 < M; i1++) {
    for (int i2 = 0; i2 < K; i2++) {
      A[i0 * 1][i1 * 5 + 7][2] = ++s;
    }
  }
}
```

```python
array_sizes_enum = Enum(('N', 10), ('M', 20), ('K', 30), ('O', 40))
var_array = Array('A', Double, array_sizes_enum.constants)
array_subscript_template = ArrayLinearSubscriptTemplate([(1, 0), (5, 7), (0, 2), (2, 2)])
assignment_var = Double('s')
print(pass_array(var_array,
                 array_subscript_template,
                 assignment_source=IncrementPrefix(assignment_var),
                 iter_var_type=SizeT))
```
Output:
```c
for (size_t i0 = 0; i0 < N; i0++) {
  for (size_t i1 = 0; i1 < M; i1++) {
    for (size_t i2 = 0; i2 < K; i2++) {
      for (size_t i3 = 0; i3 < O; i3++) {
        A[i0 * 1][i1 * 5 + 7][2][i3 * 2 + 2] = ++s;
      }
    }
  }
}
```

#### Generating array dimensions names

Function `ctestgen.generator.generate_dim_sizes_names` designed to 
automate array dimensions names generation.
Example:
```python
print(generate_dim_sizes_names(2))
print(generate_dim_sizes_names(10))
```
Output:
```c
['N', 'M']
['N0', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9']
```
Yoy can define enum constants with this names:
```python
dims_count = 4
names = generate_dim_sizes_names(dims_count)
enum_constants = [(names[i], (i + 1) * 100) for i in range(dims_count)]
enum_example = Enum(enum_constants)
print(enum_example.get_declaration())
```
Output:
```c
enum {
  N = 100,
  M = 200,
  L = 300,
  K = 400
};
```



