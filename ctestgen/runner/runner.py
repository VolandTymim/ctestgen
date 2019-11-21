from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Dict
import json
import multiprocessing as mp

from ctestgen.runner import find_tests, \
    TestRunResult, init_failed_output_file, \
    init_successful_output_file, init_output_dir, init_metrics_output_file, \
    init_results_file, Metrics, MetricsEncoder


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
        self.global_metrics = Metrics()
        self.testsets_metrics: Dict[str, Metrics] = dict()
        self.dump_results_to_files = dump_results_to_files
        self.print_run_progress = print_run_progress
        self.print_global_metrics = print_global_metrics
        self.print_percent_step = print_percent_step
        self.print_testsets_metrics = print_testsets_metrics
        self.output_dir = None
        self.successful_output_file_path = None
        self.failed_output_file_path = None
        self.metrics_output_file_path = None
        self.results_output_file_path = None

    def _on_run_start(self, tests):
        pass

    def _on_run_finish(self, tests, global_metrics):
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
            self.successful_output_file_path = init_successful_output_file(tests, self.output_dir)
            self.failed_output_file_path = init_failed_output_file(tests, self.output_dir)
            self.metrics_output_file_path = init_metrics_output_file(tests, self.output_dir)
            self.results_output_file_path = init_results_file(self.output_dir)

        env = self._get_env()

        self._on_run_start(tests)

        successful_tests_output_for_file = []
        failed_tests_output_for_file = []

        for test_dir in tests.keys():
            self.testsets_metrics[test_dir] = Metrics()

        threads_pool = mp.Pool(mp.cpu_count())
        print("Using " + str(mp.cpu_count()) + " threads")

        for test_dir, test_filenames in tests.items():
            print("Tests dir: " + test_dir)
            self.testsets_metrics[test_dir].start_time = datetime.now()
            self.testsets_metrics[test_dir].tests_count = len(test_filenames)
            self._on_testdir(test_dir, test_filenames)
            test_filenames = self._filter_test_filenames(test_filenames)

            test_result_objects = [threads_pool.apply_async(self._on_test, args=(test_dir, test_filename, env))
                                   for test_filename in test_filenames]
            test_results = [r.get() for r in test_result_objects]

            for idx, test_result in enumerate(test_results):
                test_filename = test_result.test_filename
                if test_result.result_type == TestRunResult.ResultType.SUCCESS:
                    self.testsets_metrics[test_dir].successful_count += 1
                    self.testsets_metrics[test_dir].successful_tests.append(test_filename)
                    if self.dump_results_to_files:
                        successful_tests_output_for_file.append('\nTest: ' + test_filename + '\n' +
                                                                test_result.test_output + '\n')
                else:
                    self.testsets_metrics[test_dir].failed_count += 1
                    self.testsets_metrics[test_dir].failed_tests.append(test_filename)
                    if self.dump_results_to_files:
                        failed_tests_output_for_file.append('\nTest: ' + test_filename + '\n' +
                                                            test_result.test_output + '\n')
            self.testsets_metrics[test_dir].finish_time = datetime.now()
            self.global_metrics.tests_count += self.testsets_metrics[test_dir].tests_count
            self.global_metrics.successful_count += self.testsets_metrics[test_dir].successful_count
            self.global_metrics.failed_count += self.testsets_metrics[test_dir].failed_count
            self.global_metrics.successful_tests += self.testsets_metrics[test_dir].successful_tests
            self.global_metrics.failed_tests += self.testsets_metrics[test_dir].failed_tests

        threads_pool.close()
        self.global_metrics.finish_time = datetime.now()

        testsets_metrics_descriptions = []
        for test_dir in tests.keys():
            testsets_metrics_descriptions.append('Testdir: ' + test_dir + '\n' + str(self.testsets_metrics[test_dir]))

        testsets_metrics_output = ''.join(testsets_metrics_descriptions)
        if self.print_testsets_metrics:
            print(testsets_metrics_output)

        global_metrics_description = 'Global:\n' + str(self.global_metrics)
        if self.print_global_metrics:
            print(global_metrics_description)

        if self.dump_results_to_files:
            with open(self.successful_output_file_path, 'a') as successful_output_file:
                successful_output_file.write(''.join(successful_tests_output_for_file))

            with open(self.failed_output_file_path, 'a') as failed_output_file:
                failed_output_file.write(''.join(failed_tests_output_for_file))

            if self.print_testsets_metrics:
                with open(self.metrics_output_file_path, 'a') as metrics_output_file:
                    metrics_output_file.write(testsets_metrics_output + '\n')

            if self.print_global_metrics:
                with open(self.metrics_output_file_path, 'a') as metrics_output_file:
                    metrics_output_file.write(global_metrics_description + '\n')

            with open(self.results_output_file_path, 'w') as results_output_file:
                json.dump(self.global_metrics, results_output_file, cls=MetricsEncoder)

        self._on_run_finish(tests, self.global_metrics)
