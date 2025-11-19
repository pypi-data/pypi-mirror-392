"""untility functions for dynamic type checking"""
import numpy
import pandas
import pint_pandas
import uncertainties
from fireworks.utilities.fw_serializers import FWSerializable
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.errors import RuntimeTypeError
from virtmat.language.utilities.types import NA, NC, ScalarBoolean, ScalarString
from virtmat.language.utilities.types import is_array_type, is_array, is_scalar
from virtmat.language.utilities.types import is_numeric, is_numeric_type
from virtmat.language.utilities.typemap import typemap, DType, table_like_type
from virtmat.language.utilities.units import ureg


def _rt_type_error(func):
    """wrap dynamic type checkers"""

    def wrapper(*args, **kwargs):
        try:
            assert func(*args, **kwargs) is None
        except AssertionError as err:
            raise RuntimeTypeError(str(err)) from err

    return wrapper


@_rt_type_error
def _check_datatype(rval, datatype):
    """
    Check datatype at run time (dynamic type checking, allows upcasting)

    Args:
        rval (object): value to typecheck
        datatype (type | None): datatype used for check

    Raises:
        RuntimeTypeError: is case of type mismatch
    """
    if datatype is None:
        return
    assert isinstance(datatype, type), f'datatype must be a type but is {type(datatype)}'
    if datatype is typemap['Any']:
        return
    if isinstance(rval, numpy.ndarray):
        msg = (f'datatype must be {formatter(datatype)} but is '
               f'{formatter(rval.dtype.type)}')
        assert issubclass(rval.dtype.type, datatype), msg
    elif isinstance(rval, ureg.Quantity):
        if isinstance(rval.magnitude, numpy.ndarray):
            msg = (f'datatype must be {formatter(datatype)} but is '
                   f'{formatter(rval.magnitude.dtype.type)}')
            assert issubclass(rval.magnitude.dtype.type, datatype), msg
        elif isinstance(rval.magnitude, uncertainties.UFloat):
            msg = (f'datatype must be {formatter(datatype)} but is '
                   f'{formatter(type(rval.magnitude.n))}')
            assert isinstance(rval.magnitude.n, datatype), msg
            msg = (f'datatype must be {formatter(datatype)} but is '
                   f'{formatter(type(rval.magnitude.s))}')
            assert isinstance(rval.magnitude.s, datatype), msg
        else:
            if rval.magnitude is not NA:
                msg = (f'datatype must be {formatter(datatype)} but is '
                       f'{formatter(type(rval.magnitude))}')
                assert isinstance(rval.magnitude, datatype), msg
    elif isinstance(rval, pandas.Series):
        if rval.dtype.type is numpy.object_:
            val = next((v for v in rval if v is not NA), None)
            if val is not None:
                msg = (f'datatype must be {formatter(datatype)} but is '
                       f'{formatter(type(val))}')
                if isinstance(datatype, DType):
                    _check_type_(val, datatype)
                elif datatype is typemap['Boolean']:
                    assert isinstance(val, ScalarBoolean), msg
                elif datatype is typemap['String']:
                    assert isinstance(val, ScalarString), msg
                elif is_numeric_type(datatype):
                    assert (isinstance(val, typemap['Quantity']) and
                            isinstance(val.magnitude, datatype)), msg
                else:
                    assert isinstance(val, datatype), msg  # not covered
        elif is_numeric_type(datatype):
            assert is_numeric(rval), 'datatype must be numeric'
            assert isinstance(rval.dtype, pint_pandas.PintType), f'{rval}'
            msg = (f'datatype must be {formatter(datatype)} but is '
                   f'{formatter(rval.dtype.subdtype.type)}')
            if is_array_type(datatype):
                assert issubclass(rval.dtype.subdtype.type, numpy.object_), msg
            else:
                assert issubclass(rval.dtype.subdtype.type, datatype), msg
        else:
            msg = (f'datatype must be {formatter(datatype)} but is '
                   f'{formatter(rval.dtype.type)}')
            assert issubclass(rval.dtype.type, datatype), msg


@_rt_type_error
def _check_type_(rval, type_):
    """
    Check type at run time (dynamic type checking)

    Args:
        rval (Any): value to typecheck
        type_ (type): type used for check; can be DType, str, bool or object

    Raises:
        RuntimeTypeError: is case of type mismatch
    """
    assert isinstance(type_, type)
    assert rval is not None
    if rval is NC or rval is NA or type_ is typemap['Any']:
        return
    if type_ is typemap['FuncType']:
        return
    rval_type = type(rval)
    if isinstance(rval, FWSerializable):
        rval_type = next(b for b in type(rval).__bases__ if b is not FWSerializable)
    msg = f'type must be {formatter(type_)} but is {formatter(rval_type)}'
    if type_ is typemap['Boolean']:
        assert isinstance(rval, ScalarBoolean), msg
    elif type_ is typemap['String']:
        assert isinstance(rval, ScalarString), msg
    elif issubclass(type_, ureg.Quantity):
        assert isinstance(rval, ureg.Quantity), msg
        if is_array_type(type_):
            assert is_array(rval), 'type must be Array'
        else:
            assert is_scalar(rval), 'type must be Quantity'
    elif issubclass(type_, numpy.ndarray):  # bare arrays (bool, str, numeric)
        assert is_array(rval), 'type must be Array'
    elif issubclass(type_, typemap['Tuple']):
        assert isinstance(rval, (list, tuple)), 'type must be Tuple'
    elif isinstance(rval, FWSerializable):
        assert issubclass(type_, type(rval).__bases__), msg
    else:
        assert issubclass(type_, type(rval)), msg
    _check_datatype(rval, getattr(type_, 'datatype', None))


@_rt_type_error
def _check_datatypes(rval, datatypes):
    """check the datatypes, a tuple of types"""
    if datatypes is None:
        return
    assert isinstance(datatypes, tuple)
    if not datatypes:
        return
    assert isinstance(rval, (tuple, list, dict, *table_like_type)), (
        'value must be tuple, dict or table-like')
    msg = 'lengths of datatypes mismatch'
    for val, dty in zip(rval, datatypes):
        if isinstance(rval, (tuple, list)):
            assert len(rval) == len(datatypes), msg
            _check_type_(val, dty)
        elif isinstance(rval, pandas.DataFrame):
            assert len(rval.columns) == len(datatypes), msg
            _check_type_(rval[val], dty)
        elif isinstance(rval, dict):
            assert len(rval) == len(datatypes), msg
            _check_type_(rval[val], dty)
        else:
            pass  # table-like-type not implemented


@_rt_type_error
def _check_datalen(rval, datalen):
    """check datalen at run time"""
    rval_type = formatter(type(rval))
    if datalen is None:
        iterable_types = (pandas.Series, numpy.ndarray, *table_like_type)
        msg = f'type {rval_type} must have datalen'
        assert not isinstance(rval, iterable_types), msg
        if isinstance(rval, ureg.Quantity):
            msg = f'type {formatter(type(rval.magnitude))} must have datalen'
            assert not isinstance(rval.magnitude, numpy.ndarray), msg
        return
    msg_dlt = f'invalid datalen type for type {rval_type}: {formatter(type(datalen))}'
    if isinstance(rval, (pandas.Series, *table_like_type)):
        if datalen is NA:
            return
        assert isinstance(datalen, int), msg_dlt
        msg = f'datalen of {rval_type} must be {datalen} but is {len(rval)}'
        assert len(rval) == datalen, msg
    else:
        assert isinstance(datalen, tuple), msg_dlt
        if datalen == tuple():
            return
        if isinstance(rval, numpy.ndarray):
            shape = rval.shape
        else:
            msg = f'type {rval_type} may have no datalen'
            assert isinstance(rval, ureg.Quantity), msg
            assert isinstance(rval.magnitude, numpy.ndarray), msg
            shape = rval.magnitude.shape
        msg = f'datalen of {rval_type} must be {datalen} but is {shape})'
        assert len(datalen) == len(shape), msg
        for dlen, vlen in zip(datalen, shape):
            if dlen is not NA:
                assert dlen == vlen, msg


def checktype_value(func):
    """
    Wrap a function to check the type of its returned value at run time

    func: a "value" method of a metamodel class
    obj: an instance of a metamodel class

    Returns: a wrapped func
    """
    def wrapper(obj):
        retval = func(obj)
        assert retval is not None
        if retval is NC or retval is NA or obj.type_ is typemap['Any']:
            return retval
        _check_type_(retval, obj.type_)
        _check_datatypes(retval, obj.datatypes)
        _check_datalen(retval, obj.datalen)
        return retval
    return wrapper


def checktype_func(func):
    """
    Wrap a function to check the type of its returned value at run time

    func: a "func" method of a metamodel class
    obj: an instance of a metamodel class

    Returns: a wrapped func
    """
    def wrapper(obj):
        ret_func, pars = func(obj)
        type_ = obj.type_
        datatypes = obj.datatypes
        datalen = obj.datalen

        def new_ret_func(*args, **kwargs):
            retval = ret_func(*args, **kwargs)
            assert retval is not None
            if retval is NC or retval is NA or type_ is typemap['Any']:
                return retval
            _check_type_(retval, type_)
            _check_datatypes(retval, datatypes)
            _check_datalen(retval, datalen)
            return retval
        return new_ret_func, pars
    return wrapper
