from ctestgen.generator import *


class ExampleTestGenerator(TestGenerator):
    def _generate_programs(self):
        generated_programs = list()
        for i in range(2, 6):
            sum_arguments = [Int('num_' + str(arg_idx)) for arg_idx in range(i)]
            sum_function = Function('sum_' + str(i) + '_nums', Int, sum_arguments)
            sum_result = Int('sum')
            sum_body = CodeBlock(
                Assignment(VarDeclaration(sum_result), Add(sum_arguments)),
                Return(sum_result)
            )
            sum_function.set_body(sum_body)
            example_program = Program('sum_' + str(i))
            example_program.add_function(sum_function)
            generated_programs.append(example_program)
        return generated_programs


example_generator = ExampleTestGenerator('example_generator_output')
example_generator.run()
