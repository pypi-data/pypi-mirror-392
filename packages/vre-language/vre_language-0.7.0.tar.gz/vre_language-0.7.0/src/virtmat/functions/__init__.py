"""
A collection with external functions

The set of supported numpy functions is taken from the dictionaries HANDLED_UFUNCS
and HANDLED_FUNCTIONS from the pint package. These contain repeated function names,
therefore an union of the two sets is taken. Furthermore, not all these functions
can be imported from numpy, therefore these are excluded. Furthermore, excluded from
support are "all" and "any" because:
  1) they contaminate the globals()
  2) clash with the texts grammar that does not allow these keywords as identifiers
The functions that are numpy.ufunc are checked for number of inputs and number of
outputs.
"""
import functools
import types
import typing
import numpy
import uncertainties
from uncertainties import UFloat
from pint.facets.numpy.numpy_func import HANDLED_UFUNCS, HANDLED_FUNCTIONS
from virtmat.language.utilities.errors import RuntimeValueError, RuntimeTypeError
from virtmat.language.utilities.units import ureg
from virtmat.language.utilities.types import is_scalar
from virtmat.functions.unumpy import unumpy_ufunc

FUNCTIONS = []


def uncquantify(func):
    """return a function operating on quantities with optional uncertainties"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """"currently only scalar magnitudes supported"""
        # kwargs are fully supported here but currently cannot be used in texts funcs
        try:
            assert all(isinstance(x, ureg.Quantity) for x in args)
            assert all(is_scalar(x.magnitude) for x in args)
        except AssertionError as err:
            raise RuntimeTypeError('only scalar quantities accepted') from err
        if isinstance(func, numpy.ufunc):
            assert len(args) == func.nin
        if all(not isinstance(x.magnitude, UFloat) for x in args):
            return func(*args, **kwargs)
        if getattr(uncertainties.unumpy, func.__name__, None):
            if isinstance(func, numpy.ufunc):
                assert func.nout == 1, f'func: {func}, nout: {func.nout}'
            return unumpy_ufunc(func.__name__, *args, **kwargs)
        msg = f'function "{func.__name__}" not suported with uncertainties'
        raise RuntimeTypeError(msg)
    if isinstance(func, numpy.ufunc):
        setattr(wrapper, 'nin', func.nin)
        setattr(wrapper, 'nout', func.nout)
    setattr(wrapper, '__name__', func.__name__)
    setattr(wrapper, '__qualname__', func.__name__)
    setattr(wrapper, '__module__', __name__)
    return wrapper


for _func_name in set(HANDLED_UFUNCS.keys()) | set(HANDLED_FUNCTIONS.keys()):
    if _func_name not in ('all', 'any'):
        if hasattr(numpy, _func_name):
            globals()[_func_name] = uncquantify(getattr(numpy, _func_name))
            FUNCTIONS.append(_func_name)
