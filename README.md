# Ctestgen
[Russian readme version](./README-ru.md)

Python lib for generating C-programms and running them by your target-program.
Designed to assist in automated testing of programs working with C-programms.

## Installation

```shell
pip3 install ctestgen
```

## Example usage

**Ctestgen** has two main use cases: C-programs generating and 
running target program with C-programs as input.

### C-programs generating

To generating programs, you need to inherit abstract class `ctestgen.generator.TestGenerator`
and reimplement method `_generate_programs()`, that returns c-programs abstract syntax trees.
Abstract syntax tree describing in OOP style, more [here](docs/generator_api.md).
Method `run()` calls `_generate_programs()` and then stores programs in output dir, 
which is defined when creating a class object: `ExampleTestGenerator('example_generator_output')`.

Describe the class, that generating programs with sum function, that takes from 2 to 5 arguments. 
Full code [here](./examples/example_test_generator.py).
Generated code [here](./examples/example_generator_output).
```python
from ctestgen.generator import TestGenerator
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
```
This generates, as example `sum_3.c`.
```c
int sum_3_nums(int num_0, int num_1, int num_2) {
  int sum = num_0 + num_1 + num_2;
  return sum;
}
```

**Generator** API documentation [here](docs/generator_api.md).
It contains wide OOP tools to describe desired C-programs.

### Tests running

To running programs, you need to inherit abstract class `ctestgen.runner.TestRunner`
and reimplement method `_on_test()`, that called on every program in defined directory.
**TestRunner** designed to run target program with every file, that contained in the target directory 
and its subdirectories
and have target file extensions, which defines in class object creation, by default it\`s `.c`.

**TestRunner** method `run()` describes testing pipeline, and class methods designed to override them in subclasses. 

Testing pipeline:
 - recursively collect test files in defined directory
 - call `_on_run_start(tests)`
 - for every dir, that contained test files, call `_on_testdir(test_dir, test_filenames)`
 - for every file in that dir, call `_on_test(test_dir, test_filename, env)`, 
 that returns object of `TestRunResults` class, that contains run result (SUCCESS or FAIL) 
 and output, that may be stored in corresponding files `success.txt` or `fail.txt`, 
 which defines by argument `dump_results_to_files` in class object creation. 
 - call `_on_run_finish(tests)`
 
 TestRunner collects metrics of successes and fails for every testset, and global metrics, 
 that stores in file `metrics.txt`.
 
In most cases it\`s enough to work with abstract class `ctestgen.runner.BasicTestRunner`, 
which takes target program arguments by argument `run_args` in class object creation.
In `_on_test(test_dir, test_filename, env)` it calls target program as subprocess, 
and pass results to method `_process_program_response(self, test_dir, test_filename, program_response)`.
So it\`s  enough to override this method in subclass.

Describe the class, that checking word *error* in target program output, test fails if it was found.
Full code [here](./examples/example_test_runner.py).
```python
from ctestgen.runner import BasicTestRunner
class ExampleTestRunner(BasicTestRunner):
    def _process_program_response(self, test_dir, test_filename, program_response):
        if 'error' in program_response[0] or 'error' in program_response[1]:
            return TestRunResult(TestRunResult.ResultType.FAIL, program_response[0] + program_response[1])
        return TestRunResult(TestRunResult.ResultType.SUCCESS, program_response[0] + program_response[1])
        
example_runner = ExampleTestRunner(['tsar'],
                                   output_base_dir='runner_output',
                                   test_filename_extensions=['.c'],
                                   test_base_dir='example_generator_output',
                                   runner_name='example_runner')
example_runner.run()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
