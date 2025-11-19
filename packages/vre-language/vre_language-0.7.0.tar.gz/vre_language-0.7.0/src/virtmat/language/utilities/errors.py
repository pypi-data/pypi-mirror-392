"""handling domain-specific errors"""
import sys
import importlib
import traceback
from textx.exceptions import TextXError, TextXSemanticError, TextXSyntaxError
from pint.errors import PintError, DimensionalityError, UndefinedUnitError
from pint.errors import OffsetUnitCalculusError
from uncertainties.core import NegativeStdDev
from ase.calculators.calculator import CalculatorSetupError
from virtmat.middleware.exceptions import ConfigurationException
from virtmat.middleware.exceptions import ResourceConfigurationError
from virtmat.language.utilities.textx import get_location_context
from virtmat.language.utilities.logging import logging, get_logger

FILE_READ_EXCEPTION_IMPORTS = {'ruamel.yaml.parser': 'ParserError',
                               'ruamel.yaml.scanner': 'ScannerError',
                               'json.decoder': 'JSONDecodeError',
                               'jsonschema.exceptions': 'ValidationError'}
file_read_exceptions = [FileNotFoundError, IsADirectoryError, PermissionError, UnicodeDecodeError]
FILE_WRITE_EXCEPTIONS = [FileExistsError, IsADirectoryError, PermissionError, UnicodeEncodeError]
for mod, exc in FILE_READ_EXCEPTION_IMPORTS.items():
    try:
        module = importlib.import_module(mod)
        class_ = getattr(module, exc)
    except ModuleNotFoundError:  # not covered
        continue
    else:
        file_read_exceptions.append(class_)
FILE_READ_EXCEPTIONS = tuple(file_read_exceptions)

MONGODB_EXCEPTION_IMPORTS = {'pymongo.errors': 'PyMongoError',
                             'bson.errors': 'InvalidDocument'}
MONGODB_EXCEPTIONS = []
for mod, exc in MONGODB_EXCEPTION_IMPORTS.items():
    try:
        module = importlib.import_module(mod)
        class_ = getattr(module, exc)
    except ModuleNotFoundError:  # not covered
        continue
    else:
        MONGODB_EXCEPTIONS.append(class_)


class _ErrorHandlerOptions:
    """global settings for the error handler"""
    __raise_err = False

    @property
    def raise_err(self):
        """tells the error handler whether to raise or to format and print"""
        return self.__raise_err

    @raise_err.setter
    def raise_err(self, val):
        assert isinstance(val, bool)
        self.__raise_err = val


ERROR_HANDLER_OPTIONS = _ErrorHandlerOptions()


class CompatibilityError(Exception):
    """raise this exception if grammar, data schema or python versions are incompatible"""


class InvalidUnitError(RuntimeError):
    """raise this exception if an invalid unit is detected"""


class ConvergenceError(RuntimeError):
    """raise this exception if a calculation has not converged"""


class StructureInputError(RuntimeError):
    """raise this exception if any exceptions are raised by ase.io.read"""


class StaticTypeError(Exception):
    """raise this exception if an invalid type is detected"""


class StaticValueError(Exception):
    """raise this exception if an invalid value is detected"""


class RuntimeTypeError(Exception):
    """raise this exception if an invalid type is detected at run time"""


class RuntimeValueError(Exception):
    """raise this exception if an invalid value is detected at run time"""


class PropertyError(Exception):
    """raise this exception if an error with accessing a property occurs"""


class SubscriptingError(Exception):
    """raise this exception if an error with a subscript occurs"""


class EvaluationError(Exception):
    """raised if an exception has been raised during evaluation"""


class AncestorEvaluationError(Exception):
    """raised if an exception has been raised during evaluation of ancestors"""


class ModelNotFoundError(Exception):
    """raise this exception if a model cannot be found on persistent storage"""


class VaryError(Exception):
    """raise this exception for any errors related to vary statements"""


class TagError(Exception):
    """raise this exception for any errors related to tag statements"""


class QueryError(Exception):
    """raise this exception for any errors related to query statements"""


class ReuseError(Exception):
    """raise this exception for any errors related to submodel reuse"""


class UpdateError(Exception):
    """raise this exception for errors related to variable update / rerun """


class ConfigurationError(Exception):
    """raise this exception if critical parameters are missing or invalid"""


class ObjectImportError(Exception):
    """raise this exception if an object cannot be imported"""


class ParallelizationError(Exception):
    """raise this error if error occurs in parallel map, reduce and filter"""


class InitializationError(TextXError):
    """raise this exception in case of variable initialization errors"""

    def __init__(self, obj):
        err_type = 'Initialization error'
        msg = f'Repeated initialization of "{obj.name}"'
        super().__init__(msg, **get_location_context(obj), err_type=err_type)


class CyclicDependencyError(TextXError):
    """raise this exception if a cyclic dependency is detected"""

    def __init__(self, var, ref):
        err_type = 'Cyclic dependency'
        msg1 = format_textxerr_msg(TextXError('', **get_location_context(var)))
        msg2 = format_textxerr_msg(TextXError('', **get_location_context(ref)))
        msg = f'Cycle detected:\n    Variable: {msg1}\n    Reference: {msg2}'
        super().__init__(msg, **get_location_context(ref), err_type=err_type)


class NonCallableImportError(TextXError):
    """raise this exception if an imported object is not callable"""

    def __init__(self, obj):
        err_type = 'Non-callable import'
        obj_namespace = '.'.join(obj.namespace)
        message = f'Imported object is not callable: "{obj_namespace}.{obj.name}"'
        super().__init__(message, **get_location_context(obj), err_type=err_type)


class ExpressionTypeError(TextXError):
    """raise this exception if an invalid type is used in an expression"""

    def __init__(self, obj):
        self.obj = obj
        err_type = 'Expression type error'
        message = 'Invalid type in expression'
        super().__init__(message, **get_location_context(obj), err_type=err_type)


class TypeMismatchError(TextXError):
    """raise this exception if two objects have incompatible types"""

    def __init__(self, obj1, obj2):
        err_type = 'Type mismatch error'
        msg1 = format_textxerr_msg(TextXError('', **get_location_context(obj1)))
        msg2 = format_textxerr_msg(TextXError('', **get_location_context(obj2)))
        message = ('Type mismatch:\n    ' +
                   repr(obj1.type_.__name__).strip(r"'") + ': ' + msg1 + '\n    ' +
                   repr(obj2.type_.__name__).strip(r"'") + ': ' + msg2)
        super().__init__(message, **get_location_context(obj1), err_type=err_type)


class IterablePropertyError(TextXError):
    """raise this exception if an iterable does not have a property"""

    def __init__(self, obj, obj_type, prop):
        err_type = 'Iterable property error'
        message = f'Parameter of type {obj_type} has no property "{prop}"'
        super().__init__(message, **get_location_context(obj), err_type=err_type)


class ObjectFromFileError(Exception):
    """to be raised if the causing exception is in FILE_READ_EXCEPTIONS"""

    def __init__(self, msg, path):
        self.path = path
        super().__init__(msg)

    def __str__(self):
        cause_cls = self.__cause__.__class__.__qualname__
        cause_mod = self.__cause__.__class__.__module__
        return f'{cause_mod}.{cause_cls}: {self.path}\n{self.__cause__}'

    def __reduce__(self):
        return (self.__class__, (*self.args, self.path), {'__cause__': self.__cause__})


def print_traceback():
    """optionally print the traceback"""
    if get_logger(__name__).getEffectiveLevel() == logging.DEBUG:
        traceback.print_exception(*sys.exc_info(), file=sys.stderr)


def check_raise(err, err_type=None):
    """depending on the error handler option raise_err raise the error"""
    if ERROR_HANDLER_OPTIONS.raise_err:
        err.err_type = err_type
        raise err


def textxerror_wrap(func):
    """
    This is a decorator similar to the 'textxerror_wrap' from textX but it also
    sets the error context and accepts arbitrary list of arguments. The first
    positional argument must be a textX model object.
    """
    def wrapper(*args, **kwargs):
        obj = args[0]
        try:
            return func(*args, **kwargs)
        except Exception as err:
            if isinstance(err, TextXError):
                raise
            raise TextXError(str(err), **get_location_context(obj)) from err
    return wrapper


def format_textxerr_msg(err):
    """format a TextXError message"""
    if not isinstance(err, TextXError):
        return str(err)
    msg = str(err.filename) + ':' + str(err.line) + ':' + str(err.col)
    if err.context:
        msg += ' --> ' + err.context + ' <--'
    if err.message:
        msg += '\n' + err.message
    return msg


@textxerror_wrap
def raise_exception(_, exception, msg, where_used=None):
    """utility function to raise an exception at a custom location"""
    if where_used is not None:
        err = TextXError('', **get_location_context(where_used))
        msg += f'\n    used here: {format_textxerr_msg(err)}'
    raise exception(msg)


TEXTX_WRAPPED_EXCEPTIONS = (DimensionalityError, UndefinedUnitError, PintError,
                            InvalidUnitError, CalculatorSetupError, StructureInputError,
                            StaticTypeError, RuntimeTypeError, StaticValueError,
                            RuntimeValueError, PropertyError, SubscriptingError,
                            EvaluationError, AncestorEvaluationError, ObjectFromFileError,
                            ObjectImportError, ArithmeticError, FileExistsError, OSError)


def get_err_type(err):
    """process any exception and return a domain-specific error type"""
    err_map = (('Syntax error', TextXSyntaxError),
               ('Semantic error', TextXSemanticError),
               ('Dimensionality error', DimensionalityError),
               ('Undefined unit', UndefinedUnitError),
               ('Offset unit calculus error', OffsetUnitCalculusError),
               ('Units error', PintError),
               ('Invalid units error', InvalidUnitError),
               ('Calculator setup error', CalculatorSetupError),
               ('Structure input error', StructureInputError),
               ('Type error', (StaticTypeError, RuntimeTypeError)),
               ('Value error', (StaticValueError, RuntimeValueError)),
               ('Invalid key', PropertyError),
               ('Invalid index', SubscriptingError),
               ('Convergence error', ConvergenceError),
               ('Evaluation error', EvaluationError),
               ('Ancestor evaluation error', AncestorEvaluationError),
               ('Variable update error', UpdateError),
               ('Tag error', TagError),
               ('Resource configuration error', ResourceConfigurationError),
               ('Data input error', ObjectFromFileError),
               ('Import error', ObjectImportError),
               ('Arithmetic error', ArithmeticError),
               ('Uncertainty error', NegativeStdDev),
               ('Not implemented', NotImplementedError),
               ('File exists error', FileExistsError),
               ('Operating system error', OSError),
               ('Compatibility error', CompatibilityError),
               ('Vary error', VaryError),
               ('Query error', QueryError),
               ('Reuse error', ReuseError),
               ('Model not found', ModelNotFoundError),
               ('Configuration error', ConfigurationError),
               ('Configuration error', ConfigurationException))
    if not isinstance(err, TextXError):
        for msg, cls in err_map:
            if isinstance(err, cls):
                return msg
        if isinstance(err, (*MONGODB_EXCEPTIONS, *FILE_READ_EXCEPTIONS)):
            return f'{err.__class__.__module__}.{err.__class__.__qualname__}'
        return None
    if err.err_type is None:
        for msg, cls in err_map:
            if isinstance(err, cls):
                return msg
        for msg, cls in err_map:
            if isinstance(err.__cause__, cls):
                return msg
        return f'Unknown error: {err.__cause__.__class__.__name__}'
    return err.err_type


def error_handler(func):
    """error handler decorator function"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            err_type = get_err_type(err)
            if err_type is None:
                raise RuntimeError('non-handled exception') from err
            check_raise(err, err_type)
            print_traceback()
            err_msg = format_textxerr_msg(err)
        print(f'{err_type}: {err_msg}', file=sys.stderr)
        return None
    return wrapper
