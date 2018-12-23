from abc import ABCMeta, abstractmethod
from datetime import datetime

from ctestgen.runner import find_tests,\
    get_metrics_description, TestRunResult, init_fail_output_file, \
    init_success_output_file, init_output_dir, init_metrics_output_file


class TestRunner(metaclass=ABCMeta):
    def __init__(self,
                 test_base_dir,
                 runner_name=None,
                 output_base_dir='runner_output',
                 test_filename_extensions=None,
                 dump_results_to_files=True,
                 print_run_progress=True,
                 print_percent_step=10,
                 print_global_metrics=True,
                 print_testsets_metrics=True):
        self.test_base_dir = test_base_dir
        self.runner_name = runner_name if runner_name is not None else str(self.__class__)
        self.output_base_dir = output_base_dir
        self.test_filename_extensions = test_filename_extensions \
            if test_filename_extensions is not None else ['.c']
        self.global_metrics = dict()
        self.testsets_metrics = dict()
        self.dump_results_to_files = dump_results_to_files
        self.print_run_progress = print_run_progress
        self.print_global_metrics = print_global_metrics
        self.print_percent_step = print_percent_step
        self.print_testsets_metrics = print_testsets_metrics
        self.output_dir = None
        self.success_output_file_path = None
        self.fail_output_file_path = None
        self.metrics_output_file_path = None

    def _on_run_start(self, tests):
        pass

    def _on_run_finish(self, tests):
        pass

    def _on_testdir(self, test_dir, test_filenames):
        pass

    @staticmethod
    def _filter_test_filenames(test_filenames):
        return test_filenames

    def _get_env(self):
        return None

    @abstractmethod
    def _on_test(self, test_dir, test_filename, env) -> TestRunResult:
        pass

    def run(self):
        tests = find_tests(self.test_base_dir, self.test_filename_extensions)

        if self.dump_results_to_files:
            self.output_dir = init_output_dir(self.output_base_dir, self.runner_name)
            self.success_output_file_path = init_success_output_file(tests, self.output_dir)
            self.fail_output_file_path = init_fail_output_file(tests, self.output_dir)
            self.metrics_output_file_path = init_metrics_output_file(tests, self.output_dir)

        env = self._get_env()

        self._on_run_start(tests)

        self.global_metrics['tests_count'] = 0
        self.global_metrics['success_count'] = 0
        self.global_metrics['fail_count'] = 0
        self.global_metrics['success_tests'] = list()
        self.global_metrics['fail_tests'] = list()
        self.global_metrics['start_time'] = datetime.now()
        self.global_metrics['finish_time'] = None

        for test_dir in tests.keys():
            self.testsets_metrics[test_dir] = dict()
            self.testsets_metrics[test_dir]['success_count'] = 0
            self.testsets_metrics[test_dir]['fail_count'] = 0
            self.testsets_metrics[test_dir]['tests_count'] = 0
            self.testsets_metrics[test_dir]['success_tests'] = list()
            self.testsets_metrics[test_dir]['fail_tests'] = list()
            self.testsets_metrics[test_dir]['start_time'] = None
            self.testsets_metrics[test_dir]['finish_time'] = None

        for test_dir, test_filenames in tests.items():
            self.testsets_metrics[test_dir]['start_time'] = datetime.now()
            self.testsets_metrics[test_dir]['tests_count'] = len(test_filenames)
            self._on_testdir(test_dir, test_filenames)
            test_filenames = self._filter_test_filenames(test_filenames)

            current_progress_percent = 0
            test_idx = 0
            for test_filename in test_filenames:
                if self.print_run_progress:
                    if test_idx / len(test_filenames) * 100 >= current_progress_percent:
                        print('\t\t\t\t\t' + str(current_progress_percent) + '%')
                        current_progress_percent += self.print_percent_step
                    test_idx += 1

                test_result = self._on_test(test_dir, test_filename, env)
                if test_result.result_type == TestRunResult.ResultType.SUCCESS:
                    self.testsets_metrics[test_dir]['success_count'] += 1
                    self.testsets_metrics[test_dir]['success_tests'].append(test_filename)
                    if self.dump_results_to_files:
                        with open(self.success_output_file_path, 'a') as success_output_file:
                            success_output_file.write('\nTest: ' + test_filename + '\n' +
                                                      test_result.test_output + '\n')
                else:
                    self.testsets_metrics[test_dir]['fail_count'] += 1
                    self.testsets_metrics[test_dir]['fail_tests'].append(test_filename)
                    if self.dump_results_to_files:
                        with open(self.fail_output_file_path, 'a') as fail_output_file:
                            fail_output_file.write('\nTest: ' + test_filename + '\n' +
                                                   test_result.test_output + '\n')

            if self.print_run_progress:
                print('\t\t\t\t\t100%')
            self.testsets_metrics[test_dir]['finish_time'] = datetime.now()
            self.global_metrics['tests_count'] += self.testsets_metrics[test_dir]['tests_count']
            self.global_metrics['success_count'] += self.testsets_metrics[test_dir]['success_count']
            self.global_metrics['fail_count'] += self.testsets_metrics[test_dir]['fail_count']
            self.global_metrics['success_tests'] += self.testsets_metrics[test_dir]['success_tests']
            self.global_metrics['fail_tests'] += self.testsets_metrics[test_dir]['fail_tests']

        self.global_metrics['finish_time'] = datetime.now()

        self._on_run_finish(tests)

        testsets_metrics_description = ''
        for test_dir in tests.keys():
            testsets_metrics_description += 'Testdir: ' + test_dir + '\n'
            testsets_metrics_description += get_metrics_description(self.testsets_metrics[test_dir])
        if self.print_testsets_metrics:
            print(testsets_metrics_description)

        global_metrics_description = 'Global:\n' + \
                                     get_metrics_description(self.global_metrics)
        if self.print_global_metrics:
            print(global_metrics_description)

        if self.dump_results_to_files:
            if self.print_testsets_metrics:
                with open(self.metrics_output_file_path, 'a') as metrics_output_file:
                    metrics_output_file.write(testsets_metrics_description + '\n')
            if self.print_global_metrics:
                with open(self.metrics_output_file_path, 'a') as metrics_output_file:
                    metrics_output_file.write(global_metrics_description + '\n')
