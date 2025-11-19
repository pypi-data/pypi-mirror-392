# pylint: disable=protected-access
"""a custom implementation of unumpy functions with pint"""
from itertools import chain
from uncertainties import unumpy
from pint.facets.numpy.numpy_func import (
    get_op_output_unit,
    convert_to_consistent_units
)
from pint.facets.numpy.numpy_func import (
    _is_sequence_with_quantity_elements,
    _get_first_input_units,
    _is_quantity
)

from pint.facets.numpy.numpy_func import (
    strip_unit_input_output_ufuncs,
    matching_input_bare_output_ufuncs,
    matching_input_set_units_output_ufuncs,
    set_units_ufuncs,
    matching_input_copy_units_output_ufuncs,
    copy_units_output_ufuncs,
    op_units_output_ufuncs
)

# Perform the standard ufunc implementations based on behavior collections

UFUNC_IO_UNITS = {}

for ufunc_str in strip_unit_input_output_ufuncs:
    # Ignore units
    UFUNC_IO_UNITS[ufunc_str] = {'input_units': None, 'output_unit': None}

for ufunc_str in matching_input_bare_output_ufuncs:
    # Require all inputs to match units, but output plain ndarray/duck array
    UFUNC_IO_UNITS[ufunc_str] = {'input_units': 'all_consistent', 'output_unit': None}

for ufunc_str, out_unit in matching_input_set_units_output_ufuncs.items():
    # Require all inputs to match units, but output in specified unit
    UFUNC_IO_UNITS[ufunc_str] = {'input_units': 'all_consistent', 'output_unit': out_unit}

for ufunc_str, (in_unit, out_unit) in set_units_ufuncs.items():
    # Require inputs in specified unit, and output in specified unit
    UFUNC_IO_UNITS[ufunc_str] = {'input_units': in_unit, 'output_unit': out_unit}

for ufunc_str in matching_input_copy_units_output_ufuncs:
    # Require all inputs to match units, and output as first unit in arguments
    UFUNC_IO_UNITS[ufunc_str] = {'input_units': 'all_consistent', 'output_unit': 'match_input'}

for ufunc_str in copy_units_output_ufuncs:
    # Output as first unit in arguments, but do not convert inputs
    UFUNC_IO_UNITS[ufunc_str] = {'input_units': None, 'output_unit': 'match_input'}

for ufunc_str, unit_op in op_units_output_ufuncs.items():
    UFUNC_IO_UNITS[ufunc_str] = {'input_units': None, 'output_unit': unit_op}


def unumpy_ufunc(func_str, *args, **kwargs):
    """custom unumpy implementation of a ufunc based on behavior collections"""
    func = getattr(unumpy, func_str, None)
    assert func is not None, f'ufunc {func_str} not suported with uncertainties'

    input_units = UFUNC_IO_UNITS[func_str]['input_units']
    output_unit = UFUNC_IO_UNITS[func_str]['output_unit']

    if func_str in ['multiply', 'true_divide', 'divide', 'floor_divide']:  # not covered
        if any(not _is_quantity(arg) and _is_sequence_with_quantity_elements(arg) for arg in args):
            # the sequence may contain different units, so fall back to element-wise
            return unumpy.uarray([func(*func_args) for func_args in zip(*args)])

    first_input_units = _get_first_input_units(args, kwargs)
    if input_units == "all_consistent":  # not covered
        # Match all input args/kwargs to same units
        stripped_args, stripped_kwargs = convert_to_consistent_units(
            *args, pre_calc_units=first_input_units, **kwargs
        )
    else:
        if isinstance(input_units, str):
            # Conversion requires Unit, not str
            pre_calc_units = first_input_units._REGISTRY.parse_units(input_units)
        else:
            pre_calc_units = input_units  # not covered

        # Match all input args/kwargs to input_units, or if input_units is None,
        # simply strip units
        stripped_args, stripped_kwargs = convert_to_consistent_units(
            *args, pre_calc_units=pre_calc_units, **kwargs
        )

    # Determine result through plain numpy function on stripped arguments
    result_magnitude = func(*stripped_args, **stripped_kwargs).item()  # only scalar currently

    if output_unit is None:
        # Short circuit and return magnitude alone
        return result_magnitude  # not covered
    if output_unit == "match_input":
        result_unit = first_input_units  # not covered
    elif output_unit in (
        "sum",
        "mul",
        "delta",
        "delta,div",
        "div",
        "invdiv",
        "variance",
        "square",
        "sqrt",
        "cbrt",
        "reciprocal",
        "size",
    ):  # not covered
        result_unit = get_op_output_unit(
            output_unit, first_input_units, tuple(chain(args, kwargs.values()))
        )
    else:
        result_unit = output_unit

    return first_input_units._REGISTRY.Quantity(result_magnitude, result_unit)
