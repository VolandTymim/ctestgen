import re
from datetime import datetime
from ctestgen.generator.c_operators import Call
from typing import List


class Include:
    def __init__(self, header_name, is_local_file=False):
        self.header_name = header_name
        self.is_local_file = is_local_file

    def get_declaration(self):
        include_code = '#include '
        if self.is_local_file:
            include_code += '"' + self.header_name + '"'
        else:
            include_code += '<' + self.header_name + '>'
        include_code += '\n'
        return include_code

    def __str__(self):
        return self.get_declaration()


class Define:
    def __init__(self, macro_title, macro_body):
        self.macro_title = macro_title
        self.macro_body = str(macro_body)
        assert re.fullmatch(
            r'(?:[_a-zA-Z][_a-zA-Z0-9]*)(?:\((?:[_a-zA-Z][_a-zA-Z0-9]*)(?:, *(?:[_a-zA-Z][_a-zA-Z0-9]*))*\))?',
            self.macro_title), \
            'Incorrect define title'

        identifiers = re.findall(
            r'(?:[_a-zA-Z][_a-zA-Z0-9]*)', self.macro_title)
        self.macro_name = identifiers[0]
        self.macro_arguments = identifiers[1:]

    def get_declaration(self):
        define_code = '#define ' + \
                      self.macro_title + ' ' + \
                      str(self.macro_body) + '\n'
        return define_code

    def process_macros(self, *args):
        if args and isinstance(args[0], List):
            args = args[0]
        assert len(args) == len(self.macro_arguments), \
            'Macros arguments mismatch'
        processed_body = self.macro_body
        processed_macro_arguments = list()
        replacing_protection = str(datetime.now())
        for i in range(len(args)):
            processed_body = processed_body.replace(self.macro_arguments[i], self.macro_arguments[i] +
                                                    replacing_protection)
            processed_macro_arguments.append(self.macro_arguments[i] + replacing_protection)
        for i in range(len(args)):
            processed_body = processed_body.replace(processed_macro_arguments[i], str(args[i]))
        return processed_body

    def __str__(self):
        return self.macro_name

    def __call__(self, *args):
        if args and isinstance(args[0], List):
            args = args[0]
        return Call(self.macro_name, *args)
