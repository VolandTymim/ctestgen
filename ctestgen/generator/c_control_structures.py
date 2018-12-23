from abc import ABCMeta, abstractmethod


class ControlStructure(metaclass=ABCMeta):
    @abstractmethod
    def __str__(self):
        pass


class Loop(ControlStructure):
    @abstractmethod
    def set_body(self, code_block):
        pass

    @abstractmethod
    def __str__(self):
        pass


class For(Loop):
    def __init__(self, init, continue_condition, step, body=None):
        self.init = init
        self.continue_condition = continue_condition
        self.step = step
        self.body = body

    def set_body(self, code_block):
        self.body = code_block

    def __str__(self):
        return 'for (' + str(self.init) + \
                   '; ' + str(self.continue_condition) + \
                   '; ' + str(self.step) + \
                   ') ' + str(self.body)


class While(Loop):
    def __init__(self, continue_condition, body=None):
        self.continue_condition = continue_condition
        self.body = body

    def set_body(self, code_block):
        self.body = code_block

    def __str__(self):
        return 'while (' + str(self.continue_condition) + ') ' + str(self.body)


class If(ControlStructure):
    def __init__(self, condition, true_body=None, else_body=None):
        self.condition = condition
        self.true_body = true_body
        self.else_body = else_body

    def set_true_body(self, code_block):
        self.true_body = code_block

    def set_else_body(self, code_block):
        self.else_body = code_block

    def __str__(self):
        if_code = 'if (' + str(self.condition) + ') ' + str(self.true_body)
        if self.else_body:
            # drop last line break
            if_code = if_code[:(len(if_code)-1)]
            # if_code += (self.else_body.indent_level - 1)*indent_size*indent_char + 'else' + str(self.else_body)
            if_code += ' else ' + str(self.else_body)
        return if_code
