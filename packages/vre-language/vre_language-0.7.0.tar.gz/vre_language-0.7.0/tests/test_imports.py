"""
tests for object imports
"""
import pytest
from textx import get_children_of_type
from textx import textx_isinstance
from textx.exceptions import TextXError, TextXSyntaxError
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.errors import RuntimeTypeError, ExpressionTypeError
from virtmat.language.utilities.errors import StaticValueError, StaticTypeError
from virtmat.language.utilities.errors import NonCallableImportError, ObjectImportError


def test_function_import_two_arguments_import_error(meta_model, model_kwargs):
    """test failing function import due to invalid namespace"""
    prog_inp = 'use stdlib.log10'
    with pytest.raises(TextXError, match='Object could not be imported') as err:
        meta_model.model_from_str(prog_inp, **model_kwargs)
    assert isinstance(err.value.__cause__, ObjectImportError)


def test_function_import_two_arguments_attribute_error(meta_model, model_kwargs):
    """test failing function import due to invalid name"""
    prog_inp = 'use math.log1'
    with pytest.raises(TextXError, match='Object could not be imported') as err:
        meta_model.model_from_str(prog_inp, **model_kwargs)
    assert isinstance(err.value.__cause__, ObjectImportError)


def test_function_import_two_arguments(meta_model, model_kwargs):
    """test function import with two arguments"""
    prog_inp = 'use math.log10\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    func_imports = get_children_of_type('ObjectImport', prog)
    assert len(func_imports) == 1
    assert func_imports[0].namespace == ['math']
    assert func_imports[0].name == 'log10'


def test_imported_function_call(meta_model, model_kwargs):
    """test imported function call"""
    prog_inp = 'use sqrt from my.stdlib; a = sqrt(2)'
    msg = 'Object could not be imported: "my.stdlib.sqrt"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(prog_inp, **model_kwargs)
    assert isinstance(err.value.__cause__, ObjectImportError)


def test_imported_function_call_value(meta_model, model_kwargs):
    """test call value of imported function"""
    prog_inp = 'use math.exp; use math.log; a = exp(1.0); b = 1 - log(a)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    funcs = get_children_of_type('ObjectImport', prog)
    assert len(funcs) == 2
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 2
    exp_func_call = next(v for v in calls if v.function.name == 'exp')
    assert exp_func_call.type_ is typemap['Any']
    assert exp_func_call.value == pytest.approx(2.718281828459045)
    assert textx_isinstance(exp_func_call.parent, meta_model['Variable'])
    log_func_call = next(v for v in calls if v.function.name == 'log')
    assert issubclass(log_func_call.type_, typemap['Quantity'])
    assert log_func_call.type_.datatype is typemap['Numeric']
    assert log_func_call.value == pytest.approx(1.0)
    assert textx_isinstance(log_func_call.parent, meta_model['Operand'])
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert var_a.type_ is typemap['Any']  # unbound type because type of exp unknown
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, typemap['Quantity'])
    assert var_b.type_.datatype is typemap['Numeric']  # bound to number for log type unknown
    assert var_b.value == pytest.approx(0.0)


def test_imported_function_call_value_boolean(meta_model, model_kwargs):
    """test call value of imported function returning boolean"""
    prog_inp = 'use isclose from math; b = not isclose(1.0, 0.0)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    funcs = get_children_of_type('ObjectImport', prog)
    assert len(funcs) == 1
    calls = get_children_of_type('FunctionCall', prog)
    assert len(calls) == 1
    isclose_func_call = next(v for v in calls if v.function.name == 'isclose')
    assert issubclass(isclose_func_call.type_, typemap['Boolean'])  # because in boolean expression
    assert isclose_func_call.value is False
    assert textx_isinstance(isclose_func_call.parent, meta_model['BooleanOperand'])
    var_list = get_children_of_type('Variable', prog)
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, typemap['Boolean'])
    assert var_b.value is True


def test_non_callable_object_import(meta_model, model_kwargs):
    """test non-callable object import"""
    prog_inp = 'use math.pi\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    objs = get_children_of_type('ObjectImport', prog)
    assert len(objs) == 1
    assert objs[0].value == pytest.approx(3.141592653589793)


def test_non_callable_object_import_call_error(meta_model, model_kwargs):
    """test non-callable object import call error"""
    prog_inp = 'use math.pi; a = pi(3)\n'
    with pytest.raises(NonCallableImportError, match='Imported object is not callable'):
        meta_model.model_from_str(prog_inp, **model_kwargs)


def test_non_callable_object_import_assignment(meta_model, model_kwargs):
    """test non-callable object import with assignment"""
    prog_inp = 'use math.pi; a = pi\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    imports = get_children_of_type('ObjectImport', prog)
    assert len(var_list) == 1
    assert len(imports) == 1
    assert textx_isinstance(var_list[0].parameter, meta_model['GeneralReference'])
    assert var_list[0].parameter.ref == imports[0]
    var_list = get_children_of_type('Variable', prog)
    assert len(var_list) == 1
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])  # non-callable import has known type
    assert issubclass(var_a.type_.datatype, typemap['Float'])  # non-callable import has known type
    assert var_a.value == pytest.approx(3.141592653589793)


def test_non_callable_object_import_in_expressions(meta_model, model_kwargs):
    """test non-callable object import in expressions"""
    prog_inp = 'use pi from math; a = 2*pi; b = (0 < pi) and (pi >= 3.)\n'
    prog = meta_model.model_from_str(prog_inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    assert issubclass(var_a.type_, typemap['Quantity'])
    assert issubclass(var_a.type_.datatype, typemap['Float'])
    assert var_a.value == pytest.approx(2*3.141592653589793)
    var_b = next(v for v in var_list if v.name == 'b')
    assert issubclass(var_b.type_, typemap['Boolean'])
    assert var_b.value is True


def test_repeated_initialization_of_imports(meta_model, model_kwargs):
    """test repeated initialization of object import and imported function"""
    prog_inps = ['use math.pi; pi = 4', 'use math.log; log = 2']
    for inp, var in zip(prog_inps, ('pi', 'log')):
        with pytest.raises(TextXError, match=f'Repeated initialization of "{var}"'):
            meta_model.model_from_str(inp, **model_kwargs)


def test_import_with_missing_namespace(meta_model, model_kwargs):
    """test import with missing namespace should produce syntax error"""
    with pytest.raises(TextXSyntaxError):
        meta_model.model_from_str('use log', **model_kwargs)


def test_callable_import_type_error(meta_model, model_kwargs):
    """test a callable import calling with wrong type"""
    inp = 'use len from builtins; a = len(1)'
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_a = next(v for v in var_list if v.name == 'a')
    with pytest.raises(TextXError, match="object of type 'int' has no len()") as err:
        _ = var_a.value
    assert isinstance(err.value.__cause__, RuntimeTypeError)


def test_use_of_callable_import_in_expression(meta_model, model_kwargs):
    """test invalid use of callable import in expression"""
    inp = 'use len from builtins; a = len + 1; print(a)'
    with pytest.raises(ExpressionTypeError, match='Invalid type in expression'):
        meta_model.model_from_str(inp, **model_kwargs)


def test_use_of_callable_import_in_print(meta_model, model_kwargs):
    """test invalid evaluation of callable import"""
    inp = "use exp from virtmat.functions; print(exp)"
    ref = 'virtmat.functions.exp'
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_evaluate_imported_function_runtime_error(meta_model, model_kwargs, capsys):
    """test evaluate imported function with unknown runtime error"""
    inp = 'use randint from numpy.random; print(randint(0, 10, 5))'
    _ = meta_model.model_from_str(inp, **model_kwargs).value
    stderr = capsys.readouterr().err
    msg1 = "Unknown error:"
    msg2 = "Neither Quantity object nor its magnitude (5) has attribute 'size'"
    assert msg1 in stderr
    assert msg2 in stderr


def test_import_function_call_params_mismatch(meta_model, model_kwargs):
    """test calling imported function with wrong number of parameters"""
    inp = "use exp from virtmat.functions; print(exp())"
    msg = 'Function "exp" takes 1 parameters but 0 were given'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticValueError)


def test_import_function_call_non_scalar_params(meta_model, model_kwargs):
    """test calling imported function with wrong type of parameters"""
    inp = "use correlate from virtmat.functions; k = (k: 1, 2); a = correlate(k, k)"
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    with pytest.raises(TextXError, match='only scalar quantities accepted') as err:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err.value.__cause__, RuntimeTypeError)


def test_invalid_use_of_reference_to_callable_import(meta_model, model_kwargs):
    """test invalid use of reference to callable import"""
    inp = "use exp from math; a = exp"
    msg = 'Invalid use of reference to callable import "exp"'
    with pytest.raises(TextXError, match=msg) as err:
        meta_model.model_from_str(inp, **model_kwargs)
    assert isinstance(err.value.__cause__, StaticTypeError)


def test_import_functions_from_collection(meta_model, model_kwargs):
    """test import of functions from the collection"""
    inp = ("use exp from virtmat.functions; use around from virtmat.functions;"
           "print(info(exp)); print(around(1.47))")
    ref = ("((name: 'exp'), (type: Function), (scalar: false), (numeric: false), "
           "(datatype: null))\n1.0")
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_import_functions_from_collection_with_uncert(meta_model, model_kwargs):
    """test import of functions from the collection, call with uncertainties"""
    inp = ("use exp from virtmat.functions;"
           "use boltzmann_constant from virtmat.constants;"
           "temperature = 273.15 [K];"
           "exp_hob(ene) = exp(-ene/(boltzmann_constant*temperature));"
           "d_arg = 1.+/-0.1; d = exp(d_arg); exp_f = map(exp, (s: 0.0, 1.0));"
           "c = exp_hob(0.01+/-0.005 [eV]); cn = exp_hob(0.01[eV]);"
           "vib_enes = (v: 0.1, 0.01) [eV]; vib_hob = map(exp_hob, vib_enes)")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    var_d = next(v for v in var_list if v.name == 'd')
    assert var_d.value.magnitude.n == pytest.approx(2.718281828459045)
    assert var_d.value.magnitude.s == pytest.approx(0.2718281828459045)
    var_c = next(v for v in var_list if v.name == 'c')
    assert var_c.value.magnitude.n == pytest.approx(0.6538740729814579)
    assert var_c.value.magnitude.s == pytest.approx(0.13889609242403608)
    var_cn = next(v for v in var_list if v.name == 'cn')
    assert var_cn.value.magnitude == pytest.approx(0.6538740729814579)
    var_vib = next(v for v in var_list if v.name == 'vib_hob')
    assert var_vib.value[1].magnitude == pytest.approx(0.6538740729814579)
    var_exp_f = next(v for v in var_list if v.name == 'exp_f')
    assert var_exp_f.value[0].magnitude == pytest.approx(1.0)


def test_import_functions_from_collection_with_unsupport_uncert(meta_model, model_kwargs):
    """test import of functions from the collection, unsupported call with uncertainties"""
    inp = "use exp2 from virtmat.functions; a = exp2(1.+/-0.1)"
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = 'function "exp2" not suported with uncertainties'
    with pytest.raises(TextXError, match=msg) as err:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err.value.__cause__, RuntimeTypeError)
