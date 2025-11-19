"""
constraints applied to callable objects
"""
import inspect
from textx import get_children_of_type, get_metamodel, textx_isinstance
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from virtmat.language.utilities.errors import StaticTypeError, NonCallableImportError
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.typemap import get_basetype_from_annotation


def check_function_definition(obj, metamodel):
    """check the arguments matching in FunctionDefinition or Lambda"""
    if textx_isinstance(obj, metamodel['FunctionDefinition']):
        fname = f'function {obj.name}'
    else:
        assert textx_isinstance(obj, metamodel['Lambda'])
        fname = 'lambda function'
    if len(obj.args) == 0:
        msg = 'Function definition must have at least one argument'
        raise_exception(obj, StaticValueError, msg)
    vrefs = get_children_of_type('GeneralReference', obj.expr)
    refs = [r.ref for r in vrefs if textx_isinstance(r.ref, metamodel['Dummy'])]
    refs_uniq_names = set(ref.name for ref in refs if ref in obj.args)
    args_names = [a.name for a in obj.args]
    args_uniq_names = set(args_names)
    if len(args_names) != len(args_uniq_names):
        args_names = [a.name for a in obj.args]
        args_uniq_names = set(args_names)
        dups = ', '.join(a for a in args_uniq_names if args_names.count(a) > 1)
        message = f'Duplicate argument(s) in {fname}: {dups}'
        raise_exception(obj, StaticValueError, message)
    calls = get_children_of_type('FunctionCall', obj.expr)
    call_dummies = set()
    for call in calls:
        if not textx_isinstance(call.function, metamodel['ObjectImport']):
            for arg in call.function.args:
                call_dummies.add(arg.name)
    # assert not any(d in args_uniq_names for d in call_dummies)  # the bug has been fixed
    args_uniq_names.update(call_dummies)
    refs_uniq_names.update(call_dummies)
    if list(sorted(refs_uniq_names)) != list(sorted(args_uniq_names)):
        message = (f'Dummy variables {list(sorted(refs_uniq_names))} '
                   f'do not match arguments {list(sorted(args_uniq_names))} '
                   f'in {fname}')
        raise_exception(obj, StaticValueError, message)


def check_function_import(obj):
    """check that an imported object is callable"""
    assert textx_isinstance(obj, get_metamodel(obj)['ObjectImport'])
    if not callable(obj.value):
        raise NonCallableImportError(obj)


def check_called_function_signature(call):
    """compare the signature of a called imported function to call params"""
    func = call.function.value
    try:
        signature = inspect.signature(func)
    except ValueError:
        return
    fargs = []
    nargs = 0
    for par in signature.parameters.values():
        if par.kind in (par.POSITIONAL_ONLY, par.POSITIONAL_OR_KEYWORD, par.VAR_POSITIONAL):
            fargs.append({'name': par.name, 'type': par.annotation})
            if par.default is inspect.Signature.empty:
                nargs += 1
    if len(call.params) < nargs or len(call.params) > len(fargs):
        # nb: all var_positional args count as one, this should be fixed
        message = (f'Function "{call.function.name}" takes minimum {nargs} and '
                   f'maximum {len(fargs)} parameters but {len(call.params)} were given.')
        raise_exception(call, StaticValueError, message)
    for arg, par in zip(fargs, call.params):
        if arg['type'] is not inspect.Signature.empty:
            try:
                arg_type = get_basetype_from_annotation(arg['type'])
            except StaticTypeError:
                msg = f'Argument "{arg["name"]}" has invalid type {formatter(arg["type"])}'
                raise_exception(call, StaticTypeError, msg)
            if not issubclass(par.type_, arg_type):
                msg = (f'Argument "{arg["name"]}" must be {formatter(arg["type"])}'
                       f' but is {formatter(par.type_)}.')
                raise_exception(call, StaticTypeError, msg)


def check_function_call(obj, metamodel):
    """check a function call object"""
    if textx_isinstance(obj.function, metamodel['ObjectImport']):
        check_function_import(obj.function)  # is a valid imported function
        func = obj.function.value
        if hasattr(func, 'nin') and len(obj.params) != func.nin:  # numpy ufunc
            message = (f'Function "{obj.function.name}" takes {func.nin} '
                       f'parameters but {len(obj.params)} were given.')
            raise_exception(obj, StaticValueError, message)
        check_called_function_signature(obj)
    else:
        assert textx_isinstance(obj.function, metamodel['FunctionDefinition'])
        if len(obj.params) != len(obj.function.args):
            message = (f'Function "{obj.function.name}" takes {len(obj.function.args)} '
                       f'parameters but {len(obj.params)} were given.')
            raise_exception(obj, StaticValueError, message)


def check_functions_processor(model, metamodel):
    """model processor to check function definitions and function calls"""
    for cls in ('FunctionDefinition', 'Lambda'):
        for func in get_children_of_type(cls, model):
            check_function_definition(func, metamodel)
    for call in get_children_of_type('FunctionCall', model):
        check_function_call(call, metamodel)
