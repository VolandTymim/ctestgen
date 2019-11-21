import os
from abc import abstractmethod
from ctestgen.runner import TestRunner, get_program_response, \
    find_environment_variables, TestRunResult


class BasicTestRunner(TestRunner):
    def __init__(self, run_arguments, *args, print_test_info=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_arguments = run_arguments
        self.print_test_info = print_test_info

    def _get_env(self):
        return find_environment_variables()

    @abstractmethod
    def _process_program_response(self, test_dir, test_filename, program_response) -> TestRunResult:
        pass

    def _on_test(self, test_dir, test_filename, env):
        if self.print_test_info:
            print(test_filename)
        program_response = get_program_response(self.run_arguments + [os.path.join(test_dir, test_filename)], env)
        return self._process_program_response(test_dir, test_filename, program_response)
