import os
import json
from typing import List
from ctestgen.generator import For, Assignment, IsLess, Increment, ArrayType, Var, \
    CodeBlock, Define, EnumConstant, ConstVar, ArrayC99, Int


def pass_array(array, subscript_template, assignment_source=20, iter_var_type=Int):
    assert isinstance(array.var_type, ArrayType), \
        'Array types mismatch'

    if not iter_var_type:
        iter_var_type = array.var_type.base_type

    iter_var = Var('i0', iter_var_type)
    iter_vars = [iter_var]
    first_loop = For(Assignment(iter_var.get_declaration(), 0),
                     IsLess(iter_var, array.var_type.dimension_sizes[0]),
                     Increment(iter_var))
    prev_loop = first_loop
    for current_dim in range(1, len(array.var_type.dimension_sizes)):
        iter_var = Var('i' + str(current_dim), iter_var_type)
        iter_vars.append(iter_var)
        current_loop = For(Assignment(iter_var.get_declaration(), 0),
                           IsLess(iter_var, array.var_type.dimension_sizes[current_dim]),
                           Increment(iter_var))
        prev_loop.set_body(CodeBlock(current_loop))
        prev_loop = current_loop

    subscript_expr = subscript_template.generate_subscript(array, iter_vars)
    pass_expr = (Assignment(subscript_expr, assignment_source))
    prev_loop.set_body(CodeBlock(pass_expr))

    return first_loop


class BitVector:
    def __init__(self, num_system_base):
        self.num_system_base = num_system_base
        self.vector = 0

    def set_vector(self, vector):
        self.vector = vector

    def get_bit(self, i):
        return (self.vector // (self.num_system_base ** i)) % self.num_system_base


def write_arrays_to_json(name, output_dir, *arrays, is_function_argument=False):
    if arrays and isinstance(arrays[0], List):
        arrays = arrays[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, name + '.ans'), 'wt') as output_file:
        result_map = {'Sizes': {}, 'Accesses': {}}
        for array in arrays:
            result_map['Accesses'][array.name] = \
                [template.get_str_coefficients() for template in array.subscript_templates]
            array_sizes = []
            # contains_var_size = False
            for dim_size in array.var_type.dimension_sizes:
                if isinstance(dim_size, EnumConstant):
                    array_sizes.append(str(dim_size.value))
                elif isinstance(dim_size, ConstVar):
                    array_sizes.append(str(dim_size.init_value))
                elif isinstance(dim_size, Var):
                    array_sizes.append(dim_size.name)
                elif isinstance(dim_size, Define):
                    array_sizes.append(dim_size.process_macros())
                else:
                    array_sizes.append(str(dim_size))
            if is_function_argument or isinstance(array, ArrayC99) or \
                    (not is_function_argument and isinstance(array.var_type.dimension_sizes[0], Var)):
                array_sizes[0] = '***COULDNOTCOMPUTE***'
            result_map['Sizes'][array.name] = array_sizes

        output_file.write(json.dumps(result_map))


def generate_dim_sizes_names(dims_count):
    predefined_names = ['N', 'M', 'L', 'K', 'O']
    if dims_count <= len(predefined_names):
        return predefined_names[:dims_count]
    return ['N' + str(i) for i in range(dims_count)]
