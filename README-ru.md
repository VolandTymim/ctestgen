# Ctestgen

[English version](./README.md)

Python библиотека для генерации программ на языке Си и их запуска целевой программой.
Разработана для помощи с автоматическим тестированием программ, обрабатывающих 
программы на языке Си.

## Установка

```shell
pip3 install ctestgen
```

## Использование

**Ctestgen** создана для двух основных целей: генерация программ на языке Си
и запуск целевой программы со входом из программ на языке Си.

### Генерация Си-программ.

Для создания генератора, нужно наследовать абстрактный класс `ctestgen.generator.TestGenerator`
и переопределить метод `_generate_programs()`, возвращающий абстрактные синтаксические деревья
описываемых программ. АСТ описываются в ООП стиле, подробности [здесь](docs/generator_api.md).
Метод `run()` вызывает `_generate_programs()` и затем сохраняет полученные программы в 
выходной директории, задаваемой при создании объекта класса: 
`ExampleTestGenerator('example_generator_output')`.

Опишем класс, генерирующий программы с суммирующей функцией, принимающей на вход 
от 2 до 5 аргументов. 
Полный код [здесь](./examples/example_test_generator.py).
Сгенерированный код [здесь](./examples/example_generator_output).
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
Пример сгенерированной программы `sum_3.c`:
```c
int sum_3_nums(int num_0, int num_1, int num_2) {
  int sum = num_0 + num_1 + num_2;
  return sum;
}
```

Документация API генератора [здесь](docs/generator_api.md).
API содержит широкие ООП инструменты для описания программ на языке Си.

### Запуск тестов

Для запуска программ, необходимо наследовать абстрактный класс `ctestgen.runner.TestRunner`
и переопределить метод `_on_test()`, вызываемый для каждой программы в заданной директории. 
**TestRunner** для запуска целевой программы с каждым файлом, содержащемся в заданной директории
и ее поддиректориях, имеющим целевое расширение файла, определяемое при создании объекта класса,
по умолчанию это `.c`.

**TestRunner** метод `run()` определяет процесс тестирования и методы классы предназначены для 
их переопределения в классах-наследниках.

Процесс тестирования:
 - рекурсивный поиск тестовых файлов в заданной директории
 - вызов `_on_run_start(tests)`
 - для каждой директории, содержащей тестовые файлы вызвать `_on_testdir(test_dir, test_filenames)`
 - для каждого файла в этой директории вызов `_on_test(test_dir, test_filename, env)`, 
 возвращающую объект класса `TestRunResults`, содержащий результат запуска (SUCCESS или FAIL) 
 и вывод, который может быть сохранен соответственно в файлах `success.txt` или `fail.txt`, 
 в зависимости от параметра `dump_results_to_files` при создании объекта класса. 
 - вызов `_on_run_finish(tests)`
 
 **TestRunner** собирает метрики результатов запусков для каждой директории, содержащей тестовые файлы отдельно,
 и итоговые метрики, сохраняемые в файл `metrics.txt` в зависимости от параметра `dump_results_to_files`.
 
В большинстве случаев достаточно работать с абстрактным классом `ctestgen.runner.BasicTestRunner`,
принимающем целевую программу и ее аргументы в параметре `run_args` при создании объекта класса.
Этот класс переопределяет метод `_on_test(test_dir, test_filename, env)`, вызывая целевую программу
как подпроцесс и передавая ее вывод в новый метод 
`_process_program_response(self, test_dir, test_filename, program_response)`, который необходимо 
переопределить в классе-наследнике.

Опишем класс, проверяющий наличие слова *error* в выводе целевой программы, тест провален, если слово найдено.
Полный код [здесь](./examples/example_test_runner.py).
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

## Лицензия

Проект распространяется под лицензией MIT - смотрите файл [LICENSE](LICENSE) для деталей.
