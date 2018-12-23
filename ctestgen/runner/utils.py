import subprocess
import os
import sys
from datetime import datetime
import pathlib
import enum


def find_tests(base_dir, test_filename_extensions):
    """
    Returns dictionary that collects pairs of
    directory and test filenames from it.
    """
    tests = dict()
    for dir_description in os.walk(base_dir):
        dir_filenames = dir_description[2]
        target_filenames = set()
        if len(dir_filenames) != 0:
            for filename in dir_filenames:
                file_extension = ''.join(pathlib.Path(filename).suffixes)
                if file_extension in test_filename_extensions:
                    target_filenames.add(filename)
            if len(target_filenames) != 0:
                tests[dir_description[0]] = target_filenames
    return tests


def _get_datetime_string(current_datetime):
    return current_datetime.strftime('%Y_%m_%d_%H_%M_%S')


def _get_actual_datetime_string():
    return _get_datetime_string(datetime.now())


def init_output_dir(output_dir_base, runner_name):
    output_dir = os.path.join(output_dir_base, runner_name + '_' + _get_actual_datetime_string())
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def _init_output_text_file(filename, tests, output_dir):
    output_file_path = os.path.join(output_dir, filename)
    with open(output_file_path, 'w') as output_file:
        for test_dir in tests.keys():
            output_file.write(test_dir + '\n')
    return output_file_path


def init_success_output_file(tests, output_dir):
    success_output_filename = 'success.txt'
    return _init_output_text_file(success_output_filename, tests, output_dir)


def init_fail_output_file(tests, output_dir):
    fail_output_filename = 'fail.txt'
    return _init_output_text_file(fail_output_filename, tests, output_dir)


def init_metrics_output_file(tests, output_dir):
    metrics_output_filename = 'metrics.txt'
    return _init_output_text_file(metrics_output_filename, tests, output_dir)


def find_compiler_environment_variables():
    compiler_environment_variables = dict()
    if sys.platform == 'win32':
        vswhere_str = '"' + os.path.join('%ProgramFiles(x86)%', 'Microsoft Visual Studio', 'Installer', 'vswhere.exe') \
                      + '"\n'

        cmd_call = ["cmd", "/q", "/k", "echo off"]
        vswhere_process = subprocess.Popen(cmd_call, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                           universal_newlines=True, shell=True)
        vswhere_process.stdin.write(vswhere_str)
        vswhere_process.stdin.flush()
        vswhere_process_out, vswhere_process_err = vswhere_process.communicate()
        vswhere_process.kill()
        install_path = ''
        for line in vswhere_process_out.splitlines():
            if 'installationPath:' in line:
                install_path = line[line.find(':') + 2:]
                break

        dev_cmd_path = '"' + install_path + '\Common7\Tools\VsDevCmd.bat"\n'
        dev_cmd_process = subprocess.Popen(cmd_call, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                           universal_newlines=True, shell=True)
        dev_cmd_process.stdin.write(dev_cmd_path)
        dev_cmd_process.stdin.write('SET\n')
        dev_cmd_process_out, dev_cmd_process_err = dev_cmd_process.communicate()
        dev_cmd_process.kill()
        for line in dev_cmd_process_out.splitlines():
            if '=' in line:
                var_description = line.split('=', 1)
                compiler_environment_variables[var_description[0]] = var_description[1]
    return compiler_environment_variables


def get_program_response(args, env):
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True, env=env)
    return process.stdout, process.stderr


def _get_timedelta_string(delta):
    seconds = delta.total_seconds()
    hours = seconds // 3600
    seconds = seconds % 3600
    minutes = seconds // 60
    seconds = seconds % 60
    return str(hours) + 'h - ' + str(minutes) + 'm - ' + str(seconds) + 's'


def get_metrics_description(metrics):
    metrics_description = ''
    for metric, value in metrics.items():
        if metric != 'start_time' and metric != 'finish_time':
            metrics_description += '\t' + metric + ': ' + str(value) + '\n'
    if 'start_time' in metrics.keys() and 'finish_time' in metrics.keys():
        delta = metrics['finish_time'] - metrics['start_time']
        metrics_description += '\ttime: ' + _get_timedelta_string(delta) + '\n'
    return metrics_description


class TestRunResult:
    class ResultType(enum.Enum):
        FAIL = 0
        SUCCESS = 1
        
    def __init__(self, result_type, test_output):
        self.result_type = result_type
        self.test_output = test_output

