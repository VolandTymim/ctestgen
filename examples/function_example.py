from ctestgen.generator import *

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
