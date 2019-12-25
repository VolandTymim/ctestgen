from abc import abstractmethod
from typing import List
from ctestgen.generator import TestGenerator, generate_dim_sizes_names


class ArrayTestGenerator(TestGenerator):
    def __init__(self, output_dir, *dims_count_set):
        super().__init__(output_dir)
        if dims_count_set and isinstance(dims_count_set[0], List):
            dims_count_set = dims_count_set[0]
        self.dim_sizes_names_set = [generate_dim_sizes_names(dims_count) for dims_count in dims_count_set]

    @abstractmethod
    def _generate_programs(self):
        pass
