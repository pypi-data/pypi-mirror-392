# pylint: disable=protected-access
"""
static types evaluation and static type checks
"""
import inspect
from functools import cached_property
import ase
from textx import textx_isinstance
from textx import get_parent_of_type, get_metamodel
from virtmat.language.metamodel.function import subst
from virtmat.language.utilities.textx import isinstance_m, isinstance_r
from virtmat.language.utilities.textx import get_reference, where_used
from virtmat.language.utilities.errors import textxerror_wrap, raise_exception
from virtmat.language.utilities.errors import PropertyError, SubscriptingError
from virtmat.language.utilities.errors import StaticTypeError, StaticValueError
from virtmat.language.utilities.errors import ExpressionTypeError, TypeMismatchError
from virtmat.language.utilities.errors import IterablePropertyError
from virtmat.language.utilities.typemap import typemap, table_like_type, get_dtype
from virtmat.language.utilities.typemap import get_basetype_from_annotation
from virtmat.language.utilities.typemap import get_type_from_annotation
from virtmat.language.utilities.types import is_numeric_type, is_numeric_scalar_type
from virtmat.language.utilities.types import is_numeric_array_type, is_array_type
from virtmat.language.utilities.types import is_scalar_type, is_scalar_complextype
from virtmat.language.utilities.types import is_scalar_inttype, is_scalar_realtype
from virtmat.language.utilities.types import scalar_type, ScalarNumerical, NA
from virtmat.language.utilities.formatters import formatter
from .functions import check_function_import
from .units import check_units


def check_series_type(obj, datatypes=None):
    """check if the object is series type of the given datatypes"""
    if not issubclass(obj.type_, typemap['Series']):
        msg = 'Parameter must be series or reference to series'
        raise_exception(get_reference(obj), StaticTypeError, msg, where_used(obj))
    if datatypes:
        if (obj.type_.datatype is not typemap['Any'] and
           not issubclass(obj.type_.datatype, datatypes)):
            type_name = ' or '.join(formatter(t) for t in datatypes)
            msg = f'Series must be of type {type_name}'
            raise_exception(get_reference(obj), StaticTypeError, msg, where_used(obj))


def print_type(self):
    """check types in a print statement"""
    for par in self.params:
        _ = par.type_
    return typemap['String']


def print_parameter_type(self):
    """check types in a print parameter"""
    if self.inp_units:
        if self.param.type_ is not typemap['Any']:
            if is_numeric_type(self.param.type_) is False:  # not covered
                name = getattr(getattr(self.param, 'ref', ''), 'name', '')
                raise StaticTypeError(f'Print parameter {name} is non-numeric type')
            if self.param.type_.datatype is typemap['Integer']:
                # type upcasting integer->float because units may change
                if is_array_type(self.param.type_):
                    self._datalen = self.param.datalen
                    return get_dtype('FloatArray')
                if is_scalar_type(self.param.type_):
                    return get_dtype('Quantity', datatype=typemap['Float'])
                self._datalen = self.param.datalen
                return get_dtype('Series', datatype=typemap['Float'])
    self._datatypes = self.param.datatypes
    self._datalen = self.param.datalen
    return self.param.type_


def variable_type(self):
    """evaluate variable type"""
    self._datatypes = self.parameter.datatypes
    self._datalen = self.parameter.datalen
    return self.parameter.type_


def get_numeric_type(datatypes):
    """return datatype of factor/term/expression from its parameters datatypes"""
    if len(datatypes) == 0:  # not covered
        return typemap['Numeric']
    if typemap['Any'] in datatypes:
        datatypes.discard(typemap['Any'])
        if any(is_scalar_complextype(t) for t in datatypes):  # not covered
            datatype = typemap['Complex']
        else:
            datatype = typemap['Numeric']
    elif all(is_scalar_inttype(t) for t in datatypes):
        datatype = typemap['Integer']
    elif all(is_scalar_realtype(t) or is_scalar_inttype(t) for t in datatypes):
        datatype = typemap['Float']
    elif any(is_scalar_complextype(t) for t in datatypes):
        datatype = typemap['Complex']
    else:
        assert all(is_numeric_scalar_type(t) for t in datatypes)
        datatype = typemap['Numeric']
    return datatype


def expression_type(self):
    """evaluate expression type"""
    for operand in self.operands:
        if operand.type_ is not typemap['Any'] and not is_numeric_scalar_type(operand.type_):
            raise ExpressionTypeError(operand)  # not covered
    datatypes = set(o.type_.datatype for o in self.operands if o.type_ is not typemap['Any'])
    return get_dtype('Quantity', datatype=get_numeric_type(datatypes))


def term_type(self):
    """evaluate term type"""
    for operand in self.operands:
        if operand.type_ is not typemap['Any'] and not is_numeric_scalar_type(operand.type_):
            raise ExpressionTypeError(operand)  # not covered
    datatypes = set(o.type_.datatype for o in self.operands if o.type_ is not typemap['Any'])
    if '/' in self.operators and typemap['Any'] not in datatypes:
        if all(is_scalar_realtype(t) or is_scalar_inttype(t) for t in datatypes):
            datatype = typemap['Float']
        elif any(is_scalar_complextype(t) for t in datatypes):  # not covered
            datatype = typemap['Complex']
        else:  # not covered
            datatype = typemap['Numeric']
    else:
        datatype = get_numeric_type(datatypes)
    return get_dtype('Quantity', datatype=datatype)


def factor_type(self):
    """evaluate factor type"""
    for operand in self.operands:
        if operand.type_ is typemap['Any']:
            return get_dtype('Quantity', datatype=operand.type_)
        if not is_numeric_scalar_type(operand.type_):
            raise ExpressionTypeError(operand)
    datatypes = [o.type_.datatype for o in self.operands]
    if all(issubclass(d, typemap['Integer']) for d in datatypes):
        for operand in self.operands[1:]:
            operand_obj = get_reference(operand.operand.operand)
            if isinstance_m(operand_obj, ('Quantity',)):
                val = operand_obj.inp_value and operand_obj.inp_value.value
                assert val is not None
                if operand.sign == '-':
                    val *= -1
                if val < 0:
                    return get_dtype('Quantity', datatype=typemap['Float'])
        datatype = typemap['Integer']
    else:
        datatype = get_numeric_type(set(datatypes))
    return get_dtype('Quantity', datatype=datatype)


def power_type(self):
    """evaluate power type"""
    return self.operand.type_


def operand_type(self):
    """evaluate operand type"""
    return self.operand.type_


def boolean_expression_type(self):
    """evaluate boolean expression type"""
    if hasattr(self, 'operand'):
        if not issubclass(self.operand.type_, typemap['Boolean']):
            if self.operand.type_ is not typemap['Any']:
                raise ExpressionTypeError(self.operand)
    else:
        assert hasattr(self, 'operands')
        if not all(issubclass(o.type_, typemap['Boolean']) for o in self.operands):
            oper = next(o for o in self.operands if not issubclass(o.type_, typemap['Boolean']))
            raise ExpressionTypeError(oper)  # not covered
    return typemap['Boolean']


def real_imag_type(self):
    """evaluate the type of real/imag object"""
    if self.parameter.type_ is typemap['Any']:  # not covered
        self.parameter.type_ = get_dtype('Quantity', datatype=typemap['Complex'])
        return get_dtype('Quantity', datatype=typemap['Float'])
    if issubclass(self.parameter.type_, typemap['Quantity']):
        if self.parameter.type_.datatype in (typemap['Any'], typemap['Numeric']):
            # it would make sense to also set the type of the parameter here to complex
            return get_dtype('Quantity', datatype=typemap['Float'])  # not covered
        if not issubclass(self.parameter.type_.datatype, typemap['Complex']):
            raise StaticTypeError('real/imag part only defined for complex type')  # not covered
        return get_dtype('Quantity', datatype=typemap['Float'])
    raise StaticTypeError('real/imag part only defined for quantity type')  # not covered


def if_expression_type(self):
    """evaluate if-expression type"""
    if not issubclass(self.expr.type_, typemap['Boolean']):
        raise ExpressionTypeError(self.expr)  # not covered
    if self.true_.type_ != self.false_.type_:
        raise TypeMismatchError(self.true_, self.false_)
    self._datatypes = self.true_.datatypes
    self._datalen = self.true_.datalen
    return self.true_.type_


def comparison_type(self):
    """evaluate comparison type"""
    for lrhs in (self.left.type_, self.right.type_):
        if lrhs is not typemap['Any']:
            if not issubclass(lrhs, (typemap['Boolean'], typemap['String'], typemap['Quantity'])):
                raise StaticTypeError(f'invalid type(s) used in comparison: {formatter(lrhs)}')
            if self.operator not in ('==', '!='):
                if issubclass(lrhs, (typemap['Boolean'], typemap['String'])):
                    raise StaticTypeError(f'comparison not possible with {self.operator}')
                if lrhs.datatype and is_scalar_complextype(lrhs.datatype):
                    raise StaticTypeError(f'comparison not possible with {self.operator}')
    if self.left.type_ is not typemap['Any'] and self.right.type_ is not typemap['Any']:
        if (issubclass(self.left.type_, typemap['Quantity']) and
           issubclass(self.right.type_, typemap['Quantity'])):
            return typemap['Boolean']
        if self.left.type_ != self.right.type_:
            raise TypeMismatchError(self.left, self.right)
    return typemap['Boolean']


def object_import_type(self):
    """evaluate the type of an imported object"""
    mapping = {bool: typemap['Boolean'], str: typemap['String'], int: typemap['Integer'],
               float: typemap['Float'], complex: typemap['Complex']}

    def get_import_type(obj):
        if callable(obj):
            return typemap['FuncType']
        if type(obj) in (bool, str):
            return mapping[type(obj)]  # not covered
        if isinstance(obj, typemap['Numeric']):  # bare number
            return get_dtype('Quantity', datatype=mapping[type(obj)])
        if isinstance(obj, typemap['Quantity']):  # pint quantity
            return get_dtype('Quantity', datatype=mapping[type(obj.magnitude)])
        if isinstance(obj, typemap['Series']):  # pandas series
            return get_dtype('Series', datatype=typemap['Any'])
        if isinstance(obj, (tuple, list)):
            self._datatypes = tuple(get_import_type(o) for o in obj)
            return get_dtype('Tuple')
        return typemap['Any']
    return get_import_type(self.value)


def function_call_type(self):
    """evaluate the type of a function call"""
    metamodel = get_metamodel(self)
    if textx_isinstance(self.function, metamodel['ObjectImport']):
        if textx_isinstance(self.parent, metamodel['Operand']):
            ret_type = get_dtype('Quantity', datatype=typemap['Numeric'])
        elif textx_isinstance(self.parent, metamodel['BooleanOperand']):
            ret_type = typemap['Boolean']
        elif isinstance_m(self.parent, ['Comparison']):
            other = self.parent.right if self.parent.left is self else self.parent.left
            if not ((textx_isinstance(other, metamodel['FunctionCall']) and
                     textx_isinstance(other.function, metamodel['ObjectImport'])) or
                    (textx_isinstance(other, metamodel['GeneralReference']) and
                     textx_isinstance(other.ref, metamodel['ObjectImport']))):
                if issubclass(other.type_, typemap['Quantity']):
                    ret_type = get_dtype('Quantity', datatype=typemap['Numeric'])
                else:  # not covered
                    ret_type = other.type_
            else:
                ret_type = typemap['Any']
        elif isinstance_m(self.parent, ['IfFunction', 'IfExpression']):
            other = self.parent.true_ if self.parent.false_ is self else self.parent.false_
            if not ((textx_isinstance(other, metamodel['FunctionCall']) and
                     textx_isinstance(other.function, metamodel['ObjectImport'])) or
                    (textx_isinstance(other, metamodel['GeneralReference']) and
                     textx_isinstance(other.ref, metamodel['ObjectImport']))):
                self._datatypes = other.datatypes
                self._datalen = other.datalen
                ret_type = other.type_
            else:
                ret_type = typemap['Any']
        else:
            ret_type = typemap['Any']
        annotation_dict = inspect.get_annotations(self.function.value)
        if 'return' in annotation_dict:
            if ret_type is typemap['Any']:
                ret_type = get_type_from_annotation(annotation_dict['return'])
            else:
                anno_type = get_basetype_from_annotation(annotation_dict['return'])
                if not issubclass(ret_type, anno_type):
                    msg = (f'Function call type {formatter(anno_type)} and type '
                           f'{formatter(ret_type)} of parent expression do not match.')
                    raise_exception(self, StaticTypeError, msg, where_used(self))
    else:
        assert textx_isinstance(self.function, metamodel['FunctionDefinition'])
        try:
            ret_type = self.expr.type_
        except ExpressionTypeError as err:
            raise_exception(err.obj, StaticTypeError, err.message, where_used(self))
        self._datatypes = self.expr.datatypes
        self._datalen = self.expr.datalen
    return ret_type


def tuple_type(self):
    """evaluate the types in a tuple object"""
    self._datatypes = tuple(param.type_ for param in self.params)
    return get_dtype('Tuple')


def series_type(self):
    """evaluate / check the type of a series"""
    if self.name is None:
        self._datalen = NA
        return get_dtype('Series', datatype=typemap['Any'])
    types = [elem.type_ for elem in self.elements if elem.type_ is not typemap['Any']]
    if len(set(types)) > 1:
        msg = (f'Series elements must have one type but {len(set(types))}'
               f' types were found')
        raise StaticTypeError(msg)
    self._datalen = len(self.elements)
    datatype = next(iter(types)) if len(types) > 0 else typemap['Any']
    return get_dtype('Series', datatype=datatype)


def table_type(self):
    """evaluate / check the types in a table object"""
    if self.url is not None or self.filename is not None:
        self._datatypes = tuple()
        self._datalen = NA
        return get_dtype('Table')
    names = self.get_column_names()
    if len(set(names)) != len(names):
        msg = 'Repeating column names were found in table'
        raise StaticValueError(msg)
    for column in self.columns:
        if column.type_ and not issubclass(column.type_, typemap['Series']):
            msg = 'The type of table column must be series'
            raise_exception(column, StaticTypeError, msg)
    self._datatypes = tuple(get_reference(c).type_ for c in self.columns)
    datalens = set(get_reference(c).datalen for c in self.columns)
    known_datalens = len(datalens-{None})
    if known_datalens > 1:
        msg = f'Table columns must have one size but {known_datalens} sizes were found'
        raise StaticValueError(msg)
    self._datalen = next(iter(datalens))
    return get_dtype('Table')


def dict_type(self):
    """evaluate dictionary type"""
    self._datatypes = tuple(v.type_ for v in self.values)
    return get_dtype('Dict')


def alt_table_type(self):
    """evaluate alt table type"""
    self._datalen = 1
    if self.tab:
        self._datatypes = self.tab.datatypes
        return self.tab.type_
    self._datatypes = tuple(get_dtype('Series', datatype=v.type_) for v in self.values)
    return get_dtype('Table')


def tag_type(self):
    """evaluate tag type"""
    self._datatypes = self.tagtab.datatypes
    self._datalen = self.tagtab.datalen
    return self.tagtab.type_


def get_array_datalen(obj):
    """get the axes lengths of an array object"""
    if hasattr(obj, 'elements'):
        if len(obj.elements) == 0:
            return (len(obj.elements), 0)  # not covered
        return (len(obj.elements), *get_array_datalen(obj.elements[0]))
    return tuple()


def array_type(self):
    """return array type"""
    from_file = getattr(self, 'url', None) or getattr(self, 'filename', None)
    self._datalen = tuple() if from_file else get_array_datalen(self)
    return get_dtype(self.__class__.__name__)


def get_array_type(datatype):
    """construct and return the proper array type depending on datatype"""
    if datatype is typemap['Any']:
        return typemap['Any']
    if is_array_type(datatype) and hasattr(datatype, 'datatype'):
        return get_array_type(datatype.datatype)
    try:
        return get_dtype('Array', datatype=datatype)
    except StaticTypeError as err:
        msg = 'array datatype must be numeric, boolean, string or array'
        raise StaticTypeError(msg) from err


def get_property_type(obj, type_, datalen, accessor):
    """return the type of a general reference with an optional accessor"""
    if type_ is typemap['Any']:
        return type_, datalen
    var = obj.ref
    mapping = {'IntSubArray': 'IntArray', 'FloatSubArray': 'FloatArray',
               'ComplexSubArray': 'ComplexArray', 'IntArray': 'IntArray',
               'FloatArray': 'FloatArray', 'ComplexArray': 'ComplexArray'}
    if accessor.id is not None:
        if issubclass(type_, typemap['Table']):
            if hasattr(var, 'parameter') and isinstance_r(var, ['Table']):  # table literal
                param = get_reference(var.parameter).get_column(accessor.id)
                if param is None:  # not covered
                    raise PropertyError(f'column {accessor.id} not found in Table {var.name}')
                obj._datatypes = get_reference(param).datatypes
                datalen = get_reference(param).datalen
                rettype = param.type_
            else:
                obj._datatypes = None
                rettype = get_dtype('Series', datatype=typemap['Any'])
        elif issubclass(type_, typemap['Dict']):  # not covered
            if hasattr(var, 'parameter') and isinstance_r(var, ['Dict']):  # dict literal
                assert isinstance_m(var, ['Variable'])
                dct = get_reference(var.parameter)
                elem = dict(zip(dct.keys, dct.values)).get(accessor.id)
                if elem is None:
                    msg = f'value not found for key {accessor.id} in Dict {var.name}'
                    raise PropertyError(msg)
                rettype = elem.type_
            else:
                raise PropertyError(f'Invalid key \"{accessor.id}\" in {type_.__name__}')
        elif issubclass(type_, (typemap['AMMLObject'], typemap['ChemBase'])):
            rettype = get_dtype(type_.__name__, id_=accessor.id)
            if issubclass(rettype, (typemap['Series'], *table_like_type)):
                datalen = get_reference(var.parameter).datalen
            else:
                datalen = None
            if not issubclass(rettype, (typemap['Tuple'], typemap['Dict'], *table_like_type)):
                obj._datatypes = None
            else:
                obj._datatypes = tuple()
        else:  # not covered
            raise StaticTypeError(f'Invalid use of an ID in type {type_.__name__}')
    else:
        assert accessor.index is not None
        if issubclass(type_, (typemap['Table'], typemap['Series'])):
            if datalen is not NA and not abs(accessor.index) < datalen:
                raise SubscriptingError('Index out of range')
        if issubclass(type_, (*table_like_type, typemap['AMMLTrajectory'])):
            ttypes = []
            assert get_reference(var.parameter).datatypes is not None, get_reference(var.parameter)
            for dty in get_reference(var.parameter).datatypes:
                assert issubclass(dty, typemap['Series'])
                if is_numeric_scalar_type(dty.datatype):
                    ttypes.append(get_dtype('Quantity', datatype=dty.datatype))
                elif is_numeric_array_type(dty.datatype):  # not covered
                    ttypes.append(get_dtype(mapping[dty.datatype.__name__]))
                else:  # not covered
                    ttypes.append(dty.datatype)
            obj._datatypes = tuple(ttypes)
            rettype = get_dtype('Tuple')
            datalen = None
        elif issubclass(type_, typemap['Tuple']):
            assert datalen is None
            rettype = var.datatypes[accessor.index]
            if hasattr(var, 'parameter') and isinstance_r(var, ['Tuple']):  # tuple literal
                params = get_reference(var.parameter).params
                if not abs(accessor.index) < len(params):
                    raise SubscriptingError('Index out of range')  # not covered
                obj._datatypes = params[accessor.index].datatypes
                datalen = params[accessor.index].datalen
            elif is_scalar_type(rettype):
                obj._datatypes = None
                datalen = None
            else:
                datalen = NA  # not covered
        elif issubclass(type_, typemap['Series']):
            if type_.datatype in (typemap['String'], typemap['Boolean']):
                rettype = type_.datatype
                datalen = None
            elif is_numeric_scalar_type(type_.datatype):
                rettype = get_dtype('Quantity', datatype=type_.datatype)
                datalen = None
            elif is_array_type(type_.datatype):
                if is_numeric_array_type(type_.datatype):
                    rettype = get_dtype(mapping[type_.datatype.__name__])
                else:
                    rettype = type_.datatype  # not covered
                if isinstance_m(var.parameter, ['Series']):
                    datalen = var.parameter.elements[0].datalen
                else:
                    datalen = tuple()  # not covered
            elif issubclass(type_.datatype, (typemap['Series'], *table_like_type)):
                rettype = type_.datatype
                datalen = NA
            elif type_.datatype is typemap['Any']:
                rettype = type_.datatype
                datalen = None
            elif issubclass(type_.datatype, typemap['AMMLObject']):
                rettype = type_.datatype
                datalen = None
            else:  # not covered
                msg = f'Subscripting unknown type in series: {type_.datatype.__name__}'
                raise StaticTypeError(msg)
        elif is_array_type(type_):
            assert isinstance(datalen, tuple)
            if len(datalen):
                if datalen[0] is not NA and abs(accessor.index) >= datalen[0]:
                    msg = (f'Index out of range, index: {accessor.index}, '
                           f'data length: {datalen[0]}')
                    raise SubscriptingError(msg)
                if len(datalen) > 1:
                    datalen = datalen[1:]
                    rettype = get_dtype('Array', datatype=type_.datatype)
                else:  # len(datalen) == 1
                    datalen = None
                    if is_numeric_type(type_.datatype):
                        rettype = get_dtype('Quantity', datatype=type_.datatype)
                    else:
                        rettype = type_.datatype
            else:  # empty datalen means unknown array but type may be known
                rettype = type_.datatype  # not covered
        else:  # not covered
            raise StaticTypeError(f'Invalid use of index in type {type_.__name__}')
    return rettype, datalen


def general_reference_type(self):
    """return the type of a reference to an object with optional data accessors"""
    self._datatypes = getattr(self.ref, 'datatypes', None)
    datalen = getattr(self.ref, 'datalen', None)
    type_ = self.ref.type_
    for accessor in self.accessors:
        type_, datalen = get_property_type(self, type_, datalen, accessor)
    self._datalen = datalen
    return type_


def iterable_property_type(self):
    """evaluate / check the type of an iterable property object"""

    def get_slice_size(isize, slice_obj):
        """compute the slice size from the size of an iterable"""
        try:
            return len(range(*slice_obj.indices(isize)))
        except ValueError as err:
            if 'step cannot be zero' in str(err):
                raise StaticValueError(str(err).capitalize()) from err
            raise err  # not covered

    def get_sliced_type(obj):
        """return a type slice of an iterable object but not tuple"""
        assert obj.obj.type_ is not get_dtype('Tuple')
        size_ = obj.obj.datalen
        assert size_ is not None
        if obj.slice:
            if size_ is not NA:
                size_1d = size_[0] if isinstance(size_, tuple) else size_
                sl_size = get_slice_size(size_1d, slice(obj.start, obj.stop, obj.step))
                size_ = (sl_size, *size_[1:]) if isinstance(size_, tuple) else sl_size
        if obj.array:
            obj._datalen = (size_,)
            return get_array_type(obj.obj.type_.datatype)
        obj._datatypes = obj.obj.datatypes
        obj._datalen = size_
        return get_dtype(obj.obj.type_.__name__, datatype=obj.obj.type_.datatype)

    opt_attrs = (self.array, self.columns, self.name_)
    opt_attrn = ('array', 'columns', 'name')
    if self.obj.type_ is typemap['Any']:
        ret_type = self.obj.type_
        self._datalen = self.obj.datalen
    elif issubclass(self.obj.type_, typemap['Table']):
        if self.name_:
            raise IterablePropertyError(self, 'Table', 'name')
        if self.columns:
            ret_type = get_dtype('Series', datatype=typemap['String'])
            self._datalen = len(self.obj.datatypes) or NA
        elif self.array:
            raise IterablePropertyError(self, 'Table', 'array')
        else:
            ret_type = get_sliced_type(self)
    elif issubclass(self.obj.type_, typemap['Series']):
        if self.columns:
            raise IterablePropertyError(self, 'Series', 'columns')
        ret_type = typemap['String'] if self.name_ else get_sliced_type(self)
    elif is_array_type(self.obj.type_):
        for attr, attrn in zip(opt_attrs, opt_attrn):
            if attr:
                raise IterablePropertyError(self, formatter(self.obj.type_), attrn)
        ret_type = get_sliced_type(self)
    elif is_scalar_type(self.obj.type_):
        for attr, attrn in zip(opt_attrs, opt_attrn):
            if attr:
                raise IterablePropertyError(self, formatter(self.obj.type_), attrn)
        ret_type = self.obj.type_
    elif self.obj.type_ is get_dtype('Tuple'):
        for attr, attrn in zip(opt_attrs, opt_attrn):
            if attr:
                raise IterablePropertyError(self, formatter(self.obj.type_), attrn)
        if self.slice and self.obj.datatypes:
            slice_obj = slice(self.start, self.stop, self.step)
            get_slice_size(len(self.obj.datatypes), slice_obj)
            self._datatypes = self.obj.datatypes[slice_obj]
        else:
            self._datatypes = self.obj.datatypes
        ret_type = self.obj.type_
    else:
        for attr, attrn in zip(opt_attrs, opt_attrn):
            if attr:
                raise IterablePropertyError(self, formatter(self.obj.type_), attrn)  # not covered
        ret_type = self.obj.type_
        self._datatypes = self.obj.datatypes
        self._datalen = self.obj.datalen
    return ret_type


def iterable_query_type(self):
    """evaluate / check the type of an iterable query object"""
    assert issubclass(self.obj.type_, (*table_like_type, typemap['Series']))
    if self.columns:  # "select" keyword used
        if issubclass(self.obj.type_, typemap['Series']):
            raise IterablePropertyError(self, 'Series', 'columns')  # not covered
        if isinstance_m(self.obj.ref.parameter, ['Table']):  # table literal
            columns = [self.obj.ref.parameter.get_column(c) for c in self.columns]
            self._datatypes = tuple(c.type_ for c in columns)
        else:
            self._datatypes = tuple()
    elif issubclass(self.obj.type_, table_like_type):
        self._datatypes = self.obj.datatypes
    if issubclass(self.obj.type_, table_like_type):
        datatype = None
    else:
        datatype = self.obj.type_.datatype
    self._datalen = NA if self.where else self.obj.datalen
    return get_dtype(self.obj.type_.__name__, datatype=datatype)


def check_column(pref, column):
    """check whether a GeneralReference pref contains a column (str)"""
    pref_par = pref.ref.parameter
    pref_name = pref.ref.name
    assert column is not None
    if (pref.type_ and issubclass(pref.type_, typemap['Series']) and
       isinstance_m(pref_par, ['Series'])):
        if column != pref_par.name:  # not covered
            msg = f'column \"{column}\" does not match Series name \"{pref_name}\"'
            raise StaticValueError(msg)
    if (pref.type_ and issubclass(pref.type_, typemap['Table']) and
       isinstance_m(pref_par, ['Table'])):
        if pref_par.get_column(column) is None:  # not covered
            msg = f'column \"{column}\" not found in Table \"{pref_name}\"'
            raise StaticValueError(msg)


def condition_in_type(self):
    """evaluate / check the type of condition in"""
    prop_ref = get_parent_of_type('IterableQuery', self).obj
    check_column(prop_ref, self.column)
    self._datalen = prop_ref.datalen
    return get_dtype('Series', datatype=typemap['Boolean'])


def condition_comparison_type(self):
    """evaluate / check the type of condition comparison"""
    prop_ref = get_parent_of_type('IterableQuery', self).obj
    if self.column_left is not None:
        check_column(prop_ref, self.column_left)
    if self.column_right is not None:
        check_column(prop_ref, self.column_right)
    self._datalen = prop_ref.datalen
    return get_dtype('Series', datatype=typemap['Boolean'])


def condition_not_type(self):
    """evaluate / check the type of condition NOT"""
    self._datalen = self.operand.datalen
    return get_dtype('BoolSeries')


def condition_and_type(self):
    """evaluate / check the type of condition AND"""
    assert len(set(o.datalen for o in self.operands)) == 1
    self._datalen = self.operands[0].datalen
    return get_dtype('BoolSeries')


def condition_or_type(self):
    """evaluate / check the type of condition OR"""
    assert len(set(o.datalen for o in self.operands)) == 1
    self._datalen = self.operands[0].datalen
    return get_dtype('BoolSeries')


def range_type(self):
    """evaluate / check the type of the range builtin function"""
    datatype = typemap['Float']
    for par in (self.start, self.stop, self.step):
        if par.type_ is typemap['Any']:
            continue
        if not issubclass(par.type_, typemap['Quantity']):
            raise_exception(par, StaticTypeError, 'Range parameter must be numeric type.')
        if issubclass(par.type_.datatype, typemap['Integer']):
            datatype = typemap['Integer']
        elif par.type_.datatype is typemap['Any']:
            continue
        else:
            if not issubclass(par.type_.datatype, typemap['Float']):
                raise_exception(par, StaticTypeError, 'Range parameter must be real type.')
            datatype = typemap['Float']
            break
    self._datalen = NA
    return get_dtype('Series', datatype=datatype)


def sum_type(self):
    """evaluate / check the type of the sum builtin function"""
    if self.parameter:
        if self.parameter.type_ is typemap['Any']:
            self.parameter.type_ = get_dtype('Series', datatype=typemap['Numeric'])
        else:
            check_series_type(self.parameter, (typemap['Numeric'],))
        return get_dtype('Quantity', datatype=self.parameter.type_.datatype)
    assert self.params
    if any(p.type_.datatype is typemap['Any'] for p in self.params):
        datatype = typemap['Numeric']  # not covered
    elif any(p.type_.datatype is typemap['Numeric'] for p in self.params):
        datatype = typemap['Numeric']
    elif all(issubclass(p.type_.datatype, typemap['Integer']) for p in self.params):
        datatype = typemap['Integer']
    elif any(issubclass(p.type_.datatype, typemap['Complex']) for p in self.params):
        datatype = typemap['Complex']
    else:  # not covered
        datatype = typemap['Float']
    return get_dtype('Quantity', datatype=datatype)


def get_par_datatype(obj, datatype):
    """create test params and types to determine type of map/filter/reduce"""
    if datatype and issubclass(datatype, scalar_type):
        meta = get_metamodel(obj)
        if issubclass(datatype, typemap['Boolean']):
            param = meta['Bool']()
            type_ = typemap['Boolean']
        elif issubclass(datatype, typemap['String']):  # not covered
            param = meta['String']()
            type_ = typemap['String']
        else:
            assert issubclass(datatype, ScalarNumerical)
            param = meta['Quantity']()
            param.inp_value = 0 if issubclass(datatype, typemap['Integer']) else 0.
            param.inp_units = None
            type_ = get_dtype('Quantity', datatype=datatype)
        return param, type_
    return None, typemap['Any']


def map_type(self):
    """evaluate / check the type of the map builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    if any(p.type_ is typemap['Any'] for p in self.params):
        if not isinstance_m(func.expr, ['Dict']):
            for p in self.params:
                if p.type_ is typemap['Any']:
                    p.type_ = get_dtype('Series', datatype=typemap['Any'])
    elif not all(issubclass(p.type_, (typemap['Series'], *table_like_type)) for p in self.params):
        raise StaticTypeError('map inputs must be either series or table-like')
    dsize = self.params[0].datalen
    self._datalen = dsize if not self.nchunks else NA
    if not all(p.datalen is NA or p.datalen == dsize for p in self.params):
        raise StaticValueError('map inputs must have equal size')
    if isinstance_m(func, ['ObjectImport']):
        check_function_import(func)
        return get_dtype('Series', datatype=typemap['Any'])
    if len(func.args) != len(self.params):
        raise StaticValueError('number of map function arguments and map inputs must be equal')
    if isinstance_m(func.expr, ['Dict']):
        self._datatypes = tuple()  # a better guess can be done from func
        return get_dtype('Table')
    assert all(issubclass(p.type_, typemap['Series']) for p in self.params)
    par_types = [get_par_datatype(self, p.type_.datatype) for p in self.params]
    params, types = [p for p, t in par_types], [t for p, t in par_types]
    new_type = subst(self, func, params, types).type_
    if (new_type is typemap['Any'] or
       issubclass(new_type, (typemap['Boolean'], typemap['String']))):
        return get_dtype('Series', datatype=new_type)
    return get_dtype('Series', datatype=new_type.datatype)


def filter_type(self):
    """evaluate / check the type of the filter builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    if not issubclass(self.parameter.type_, (typemap['Series'], *table_like_type)):
        raise StaticTypeError('filter input must be either series or table-like')
    self._datalen = NA
    if isinstance_m(func, ['ObjectImport']):
        check_function_import(func)
        return self.parameter.type_
    if len(func.args) != 1:
        raise StaticValueError('Filter function must have only one argument')
    if issubclass(self.parameter.type_, typemap['Series']):
        if (isinstance_m(func.expr, ['FunctionCall'])
                and isinstance_m(func.expr.function, ['ObjectImport'])):
            check_function_import(func.expr.function)
            return self.parameter.type_
        param, type_ = get_par_datatype(self, self.parameter.type_.datatype)
        if not issubclass(subst(self, func, [param], [type_]).type_, typemap['Boolean']):
            raise StaticTypeError('Filter function must be of boolean type')
        return self.parameter.type_
    self._datatypes = self.parameter.datatypes
    return self.parameter.type_


def reduce_type(self):
    """evaluate / check the type of the reduce builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    if self.parameter.type_ is typemap['Any']:
        if not issubclass(func.expr.type_, typemap['Dict']):
            self.parameter.type_ = get_dtype('Series', datatype=typemap['Any'])
    elif not issubclass(self.parameter.type_, (typemap['Series'], *table_like_type)):
        raise StaticTypeError('reduce input must be either series or table-like')
    if isinstance_m(func, ['ObjectImport']):
        check_function_import(func)
        return typemap['Any']
    if len(func.args) != 2:
        raise StaticValueError('Reduce function must have exactly two arguments')
    if issubclass(self.parameter.type_, typemap['Series']):
        if (isinstance_m(func.expr, ['FunctionCall'])
                and isinstance_m(func.expr.function, ['ObjectImport'])):  # not covered
            check_function_import(func.expr.function)
            return typemap['Any']
        param, type_ = get_par_datatype(self, self.parameter.type_.datatype)
        return subst(self, func, [param]*2, [type_]*2).type_
    self._datatypes = tuple()  # otherwise self.parameter.datatypes must be "sliced"
    self._datalen = 1
    return get_dtype('Table')


def boolean_reduce_type(self):
    """evaluate / check the type of the boolean reduce builtin function"""
    msg = 'Boolean reduce parameters must be of boolean type'
    if self.parameter is not None:
        check_series_type(self.parameter)
        if (self.parameter.type_.datatype and
           not issubclass(self.parameter.type_.datatype, typemap['Boolean'])):
            raise StaticTypeError(msg)
    else:
        if not all(issubclass(p.type_, (typemap['Boolean'], typemap['Any'])) for p in self.params):
            raise StaticTypeError(msg)  # not covered
    return typemap['Boolean']


def in_type(self):
    """evaluate / check the type of in-expression"""
    if self.parameter is not None:
        check_series_type(self.parameter)
    return typemap['Boolean']


def quantity_type(self):
    """evaluate the type of a quantity literal"""
    if self.inp_value is None:
        return get_dtype('Quantity', datatype=typemap['Numeric'])
    assert self.inp_value.type_ in typemap.values()
    if getattr(self, 'uncert', None):  # getattr to maintain compat to old grammar
        if not issubclass(self.inp_value.type_, typemap['Float']):
            raise StaticTypeError('uncertainty supported only for type Float')
        if not issubclass(self.uncert.type_, typemap['Float']):
            raise StaticTypeError('uncertainty must be type Float')
        assert isinstance_m(self.uncert, ['Number'])
        if self.uncert.value < 0:
            raise StaticValueError('uncertainty cannot be negative')
        return get_dtype('Quantity', datatype=typemap['Float'])
    return get_dtype('Quantity', datatype=self.inp_value.type_)


def amml_structure_type(self):
    """evaluate the type of structure object"""
    if self.filename or self.url:
        self._datalen = NA
        self._datatypes = tuple()
        return get_dtype('AMMLStructure')
    tab_typs = {'atoms': typemap['Table'], 'pbc': typemap['BoolArray'],
                'cell': (typemap['FloatArray'], typemap['FloatSubArray'])}
    column_names = self.tab.get_column_names()
    if 'atoms' not in column_names:  # not covered
        raise_exception(self.tab, StaticValueError, '\'atoms\' missing in \'structure\'')
    if not all(n in tab_typs for n in column_names):  # not covered
        col = next(self.tab.get_column(n) for n in column_names if n not in tab_typs)
        msg = f'invalid parameter \'{col.name}\' in \'structure\''
        raise_exception(col, StaticValueError, msg)
    for col in (self.tab.get_column(n) for n in column_names):
        if isinstance_m(col, ['Series']):
            if col.type_ and col.type_.datatype:
                if not issubclass(col.type_.datatype, tab_typs[col.name]):  # not covered
                    msg = (f'Series \'{col.name}\' must have type '
                           f'{tab_typs[col.name]} but has type {col.type_.datatype}')
                    raise_exception(col, StaticTypeError, msg)
    fquantity = typemap['Float']
    atoms_dtyps = {'symbols': typemap['String'], 'x': fquantity, 'y': fquantity, 'z': fquantity,
                   'px': fquantity, 'py': fquantity, 'pz': fquantity, 'tags': typemap['Integer'],
                   'masses': fquantity}
    atoms_col = self.tab.get_column('atoms')
    if atoms_col is not None:
        for atoms_elem in atoms_col.elements:
            atoms = get_reference(atoms_elem)
            if atoms.type_ is typemap['Any']:  # not covered
                continue
            assert issubclass(atoms.type_, typemap['Table'])
            if not isinstance_m(atoms, ['Table']):  # not covered
                continue
            for col in atoms.columns:
                if col.type_ is typemap['Any']:  # not covered
                    continue
                assert issubclass(col.type_, typemap['Series'])
                if isinstance_m(col, ['Series']):
                    if col.name not in atoms_dtyps:  # not covered
                        msg = f'invalid parameter \'{col.name}\' in \'atoms\''
                        raise_exception(col, StaticValueError, msg)
                    if not issubclass(col.type_.datatype, atoms_dtyps[col.name]):  # not covered
                        msg = (f'\'{col.name}\' must have type {atoms_dtyps[col.name]}'
                               f' but has type {col.type_.datatype}')
                        raise_exception(col, StaticTypeError, msg)
            symbols = atoms.get_column('symbols')
            if symbols:
                for elem in symbols.elements:
                    if elem.value not in ase.data.chemical_symbols:  # not covered
                        msg = f'invalid chemical symbol {elem.value} in \'symbols\''
                        raise_exception(elem, StaticValueError, msg)
            elif not atoms.columns_tuple:
                raise_exception(atoms, StaticValueError, 'missing chemical symbols')
            for column in ('x', 'y', 'z'):
                coord = atoms.get_column(column)
                if coord:
                    check_units(coord, '[length]')
                elif not atoms.columns_tuple:
                    raise_exception(atoms, StaticValueError, 'missing atomic coordinates')
            momenta = ('px', 'py', 'pz')
            if any(atoms.get_column(p) is not None for p in momenta):
                if not all(atoms.get_column(p) is not None for p in momenta):  # not covered
                    missed = next(p for p in momenta if atoms.get_column(p) is None)
                    msg = f'{missed} missing in \'atoms\''
                    raise_exception(atoms, StaticValueError, msg)
            if self.tab.get_column('cell') is not None:
                for cell_elem in self.tab.get_column('cell').elements:
                    if hasattr(get_reference(cell_elem), 'inp_units'):
                        check_units(get_reference(cell_elem), '[length]')
            if any(atoms.get_column(x) is not None for x in ('px', 'py', 'pz')):
                for column in ('px', 'py', 'pz'):
                    momentum = atoms.get_column(column)
                    if momentum is not None:
                        check_units(momentum, '[length]*[mass]/[time]')
            if atoms.get_column('masses') is not None:
                check_units(atoms.get_column('masses'), '[mass]')
    self._datalen = self.tab.datalen
    self._datatypes = self.tab.datatypes
    return get_dtype('AMMLStructure')


def amml_calculator_type(self):
    """evaluate the type of calculator object"""
    assert self.parameters is None or isinstance_m(self.parameters, ['Table'])
    self._datalen = NA if self.parameters is None else self.parameters.datalen
    self._datatypes = tuple() if self.parameters is None else self.parameters.datatypes
    return get_dtype('AMMLCalculator')


def amml_algorithm_type(self):
    """evaluate the type of algorithm object"""
    assert self.parameters is None or isinstance_m(self.parameters, ['Table'])
    self._datalen = NA if self.parameters is None else self.parameters.datalen
    self._datatypes = tuple() if self.parameters is None else self.parameters.datatypes
    return get_dtype('AMMLAlgorithm')


def amml_property_type(self):
    """evaluate the type of property object"""
    if not issubclass(self.struct.type_, typemap['AMMLStructure']):  # not covered
        msg = f'Parameter \"{self.struct.ref.name}\" must be an AMML structure'
        raise_exception(self.struct, StaticTypeError, msg)
    if self.calc and not issubclass(self.calc.type_, typemap['AMMLCalculator']):  # not covered
        msg = f'parameter \"{self.calc.name}\" must be an AMML calculator'
        raise_exception(self.calc, StaticTypeError, msg)
    if (isinstance_m(self.struct.ref.parameter, ['AMMLStructure']) and
       self.struct.ref.parameter.tab is not None):
        atoms = self.struct.ref.parameter.tab.get_column('atoms')
        if all(isinstance_m(get_reference(e), ['Table']) for e in atoms.elements):
            symbs = [get_reference(e).get_column('symbols').elements for e in atoms.elements]
            for constr in self.constrs:
                if isinstance_m(constr.ref.parameter, ['AMMLConstraint']):
                    if isinstance_m(constr.ref.parameter.fixed, ['Series']):
                        elems = constr.ref.parameter.fixed.elements
                        if not all(len(elems) == len(s) for s in symbs):
                            msg = ('The list of fixed/non-fixed atoms in constraints'
                                   ' and atoms in structure have different lengths')
                            raise StaticValueError(msg)
    if self.algo is not None:
        if not issubclass(self.algo.type_, typemap['AMMLAlgorithm']):  # not covered
            msg = f'Parameter \"{self.algo.ref.name}\" must be an AMML algorithm'
            raise_exception(self.algo, StaticTypeError, msg)
        if (isinstance_m(self.algo.ref.parameter, ['AMMLAlgorithm']) and
           self.algo.ref.parameter.name == 'RDF'):
            algo_name = self.algo.ref.parameter.name
            if (isinstance_m(self.struct.ref.parameter, ['AMMLStructure']) and
               self.struct.ref.parameter.tab is not None):
                struct_tab = self.struct.ref.parameter.tab
                if struct_tab.get_column('cell') is None:  # not covered
                    msg = f'Algorithm \"{algo_name}\" requires structure with cell'
                    raise_exception(struct_tab, StaticValueError, msg)
    self._datalen = NA  # the runtime value is len(self.value.results)
    self._datatypes = tuple()  # the runtime value in self.value.results.dtypes
    return get_dtype('AMMLProperty')


def amml_constraint_type(self):
    """evaluate the type of constraint object"""
    if self.fixed is not None:
        if self.fixed.type_:
            msg = 'parameter must be a boolean series'
            if not issubclass(self.fixed.type_, typemap['Series']):
                raise_exception(self.fixed, StaticTypeError, msg)  # not covered
            if not issubclass(self.fixed.type_.datatype, typemap['Boolean']):
                raise_exception(self.fixed, StaticTypeError, msg)  # not covered
    if self.direction is not None:
        if (not all(isinstance(e, typemap['Integer']) for e in self.direction.elements)
           or len(self.direction.elements) != 3):  # not covered
            msg = 'direction vector must be 1-dim integer array with 3 elements'
            raise_exception(self.direction, StaticTypeError, msg)
    return get_dtype('AMMLConstraint')


def check_numerical_props(tab):
    """check if a table contains only series with given names of float type"""
    keys = ['energy', 'enthalpy', 'entropy', 'free_energy', 'zpe', 'temperature']
    if tab is not None:
        if tab.columns:
            for prop in tab.columns:
                if prop.name not in keys:  # not covered
                    raise_exception(prop, StaticValueError, f'invalid property \'{prop.name}\'')
                check_series_type(prop, (typemap['Quantity'], typemap['Float']))
        if tab.columns_tuple:
            for prop in tab.columns_tuple.params:  # not covered
                check_series_type(prop, (typemap['Quantity'], typemap['Float']))


def chem_reaction_type(self):
    """evaluate the type of a chemical reaction object"""
    check_numerical_props(self.props)
    for term in self.educts + self.products:
        if not isinstance_m(term.species.ref.parameter, ['ChemSpecies']):  # not covered
            msg = f'{term.species.ref.name} is no chemical species'
            raise_exception(term, StaticTypeError, msg)
    self._datalen = NA  # the runtime value is len(self.value.props)
    self._datatypes = tuple()  # the runtime value in self.value.props.dtypes
    return get_dtype('ChemReaction')


def chem_species_type(self):
    """evaluate the type of a chemical species object"""
    if self.composition:
        if self.composition.type_ and not issubclass(self.composition.type_, typemap['String']):
            raise StaticTypeError('species composition must be of string type')
    check_numerical_props(self.props)
    self._datalen = NA  # the runtime value is len(self.value.props)
    self._datatypes = tuple()  # the runtime value in self.value.props.dtypes
    return get_dtype('ChemSpecies')


def add_type_properties(metamodel):
    """Add object class properties using monkey style patching"""
    mapping_dict = {
        'Print': print_type,
        'PrintParameter': print_parameter_type,
        'Variable': variable_type,
        'GeneralReference': general_reference_type,
        'Power': power_type,
        'Factor': factor_type,
        'Term': term_type,
        'Expression': expression_type,
        'Operand': operand_type,
        'BooleanOperand': operand_type,
        'And': boolean_expression_type,
        'Or': boolean_expression_type,
        'Not': boolean_expression_type,
        'Real': real_imag_type,
        'Imag': real_imag_type,
        'IfFunction': if_expression_type,
        'IfExpression': if_expression_type,
        'Comparison': comparison_type,
        'ObjectImport': object_import_type,
        'FunctionCall': function_call_type,
        'Quantity': quantity_type,
        'Tuple': tuple_type,
        'Series': series_type,
        'Table': table_type,
        'Dict': dict_type,
        'AltTable': alt_table_type,
        'Tag': tag_type,
        'BoolArray': array_type,
        'StrArray': array_type,
        'IntArray': array_type,
        'FloatArray': array_type,
        'ComplexArray': array_type,
        'IntSubArray': array_type,
        'FloatSubArray': array_type,
        'ComplexSubArray': array_type,
        'IterableProperty': iterable_property_type,
        'IterableQuery': iterable_query_type,
        'ConditionIn': condition_in_type,
        'ConditionComparison': condition_comparison_type,
        'ConditionNot': condition_not_type,
        'ConditionAnd': condition_and_type,
        'ConditionOr': condition_or_type,
        'Range': range_type,
        'In': in_type,
        'Any': boolean_reduce_type,
        'All': boolean_reduce_type,
        'Sum': sum_type,
        'Map': map_type,
        'Filter': filter_type,
        'Reduce': reduce_type,
        'AMMLStructure': amml_structure_type,
        'AMMLCalculator': amml_calculator_type,
        'AMMLAlgorithm': amml_algorithm_type,
        'AMMLProperty': amml_property_type,
        'AMMLConstraint': amml_constraint_type,
        'ChemReaction': chem_reaction_type,
        'ChemSpecies': chem_species_type
    }
    for key, function in mapping_dict.items():
        metamodel[key].type_ = cached_property(textxerror_wrap(function))
        metamodel[key].type_.__set_name__(metamodel[key], 'type_')
        metamodel[key].datatypes = property(lambda x: x.type_ and getattr(x, '_datatypes', None))
        metamodel[key].datalen = property(lambda x: x.type_ and getattr(x, '_datalen', None))

    metamodel['Dummy'].type_ = typemap['Any']
    metamodel['Bool'].type_ = typemap['Boolean']
    metamodel['Bool'].datatypes = None
    metamodel['Bool'].datalen = None
    metamodel['String'].type_ = typemap['String']
    metamodel['String'].datatypes = None
    metamodel['String'].datalen = None
    metamodel['Program'].type_ = typemap['String']
    metamodel['Program'].datatypes = None
    metamodel['Program'].datalen = None
    metamodel['Type'].type_ = get_dtype('Table')
    metamodel['Type'].datatypes = tuple()
    metamodel['Type'].datalen = 1
