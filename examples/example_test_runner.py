import shlex
from ctestgen.runner import BasicTestRunner
from ctestgen.runner import TestRunResult


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
