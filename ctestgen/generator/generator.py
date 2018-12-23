from abc import ABCMeta, abstractmethod
from typing import List
import os

from ctestgen.generator import Program


class TestGenerator(metaclass=ABCMeta):
    def __init__(self, output_dir):
        self.output_dir = output_dir

    @abstractmethod
    def _generate_programs(self) -> List[Program]:
        pass

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        programs = self._generate_programs()
        for program in programs:
            program.write_to_file(self.output_dir)
