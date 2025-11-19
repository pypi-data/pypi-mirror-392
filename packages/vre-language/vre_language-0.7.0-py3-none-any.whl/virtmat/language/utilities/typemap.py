"""type map and custom type definitions"""
import types
import typing
import numbers
import numpy
import pandas
from virtmat.language.utilities import amml, chemistry
from virtmat.language.utilities.units import ureg
from virtmat.language.utilities.errors import StaticTypeError
from virtmat.language.utilities.types import ScalarBoolean, ScalarString

typemap = {
    'Any': object,
    'String': str,
    'Tuple': list,
    'Dict': dict,
    'FuncType': types.FunctionType,
    'Boolean': numpy.bool,
    'Integer': numbers.Integral,
    'Float': numbers.Real,
    'Complex': numbers.Complex,
    'Numeric': numbers.Number,
    'Quantity': ureg.Quantity,
    'Table': pandas.DataFrame,
    'Series': pandas.Series,
    'BoolArray': numpy.ndarray,
    'StrArray': numpy.ndarray,
    'NumArray': ureg.Quantity,
    'IntArray': ureg.Quantity,
    'FloatArray': ureg.Quantity,
    'ComplexArray': ureg.Quantity,
    'IntSubArray': numpy.ndarray,
    'FloatSubArray': numpy.ndarray,
    'ComplexSubArray': numpy.ndarray,
    'AMMLObject': amml.AMMLObject,
    'AMMLIterableObject': amml.AMMLIterableObject,
    'AMMLStructure': amml.AMMLStructure,
    'AMMLCalculator': amml.Calculator,
    'AMMLAlgorithm': amml.Algorithm,
    'AMMLProperty': amml.Property,
    'AMMLConstraint': amml.Constraint,
    'AMMLTrajectory': amml.Trajectory,
    'ChemBase': chemistry.ChemBase,
    'ChemReaction': chemistry.ChemReaction,
    'ChemSpecies': chemistry.ChemSpecies
}

table_like_type = (pandas.DataFrame, amml.AMMLIterableObject, chemistry.ChemBase)


class DType(type):
    """
    A special metaclass to create types on the fly. These types (classes) have
    our specific attributes datatype and arraytype.

    Arguments:
        datatype: (type | None)
        arraytype: (bool)
    """
    datatype = None
    arraytype = False

    def __init__(cls, *args, **kwargs):
        def new(cls, *args, **kwargs):  # not covered, why never called?
            base_cls = cls.__bases__[0]
            obj = base_cls.__new__(base_cls, *args, **kwargs)
            obj.__class__ = cls
            return obj
        cls.__new__ = new
        super().__init__(*args, **kwargs)

    def __eq__(cls, other):
        if cls.__name__ != other.__name__:
            return False
        if set(cls.__bases__) != set(other.__bases__):
            return False  # not covered
        if cls.datatype != other.datatype:
            return False
        return cls.arraytype is other.arraytype

    def __hash__(cls):
        return hash(repr(cls))


IntQuantity = DType('IntQuantity', (typemap['Quantity'],), {'datatype': typemap['Integer']})
FloatQuantity = DType('FloatQuantity', (typemap['Quantity'],), {'datatype': typemap['Float']})
ComplexQuantity = DType('ComplexQuantity', (typemap['Quantity'],), {'datatype': typemap['Complex']})
NumericQuantity = DType('NumericQuantity', (typemap['Quantity'],), {'datatype': typemap['Numeric']})
AnyQuantity = DType('AnyQuantity', (typemap['Quantity'],), {'datatype': typemap['Any']})

StrSeries = DType('StrSeries', (typemap['Series'],), {'datatype': typemap['String']})
BoolSeries = DType('BoolSeries', (typemap['Series'],), {'datatype': typemap['Boolean']})
IntSeries = DType('IntSeries', (typemap['Series'],), {'datatype': typemap['Integer']})
FloatSeries = DType('FloatSeries', (typemap['Series'],), {'datatype': typemap['Float']})
ComplexSeries = DType('ComplexSeries', (typemap['Series'],), {'datatype': typemap['Complex']})
NumericSeries = DType('NumericSeries', (typemap['Series'],), {'datatype': typemap['Numeric']})
AnySeries = DType('AnySeries', (typemap['Series'],), {'datatype': typemap['Any']})
# workaround for a bug in series_type:
QuantitySeries = DType('QuantitySeries', (typemap['Series'],), {'datatype': typemap['Quantity']})

StrArray = DType('StrArray', (typemap['StrArray'],),
                 {'datatype': typemap['String'], 'arraytype': True})
BoolArray = DType('BoolArray', (typemap['BoolArray'],),
                  {'datatype': typemap['Boolean'], 'arraytype': True})
IntArray = DType('IntArray', (typemap['IntArray'],),
                 {'datatype': typemap['Integer'], 'arraytype': True})
FloatArray = DType('FloatArray', (typemap['FloatArray'],),
                   {'datatype': typemap['Float'], 'arraytype': True})
ComplexArray = DType('ComplexArray', (typemap['ComplexArray'],),
                     {'datatype': typemap['Complex'], 'arraytype': True})
NumArray = DType('NumArray', (typemap['NumArray'],),
                 {'datatype': typemap['Numeric'], 'arraytype': True})
IntSubArray = DType('IntSubArray', (typemap['IntSubArray'],),
                    {'datatype': typemap['Integer'], 'arraytype': True})
FloatSubArray = DType('FloatSubArray', (typemap['FloatSubArray'],),
                      {'datatype': typemap['Float'], 'arraytype': True})
ComplexSubArray = DType('ComplexSubArray', (typemap['ComplexSubArray'],),
                        {'datatype': typemap['Complex'], 'arraytype': True})

Tuple = DType('Tuple', (typemap['Tuple'],), {})
Table = DType('Table', (typemap['Table'],), {})
Dict = DType('Dict', (typemap['Dict'],), {})

AMMLStructure = DType('AMMLStructure', (typemap['AMMLStructure'],), {})
AMMLCalculator = DType('AMMLCalculator', (typemap['AMMLCalculator'],), {})
AMMLAlgorithm = DType('AMMLAlgorithm', (typemap['AMMLAlgorithm'],), {})
AMMLProperty = DType('AMMLProperty', (typemap['AMMLProperty'],), {})
AMMLConstraint = DType('AMMLConstraint', (typemap['AMMLConstraint'],), {})
AMMLTrajectory = DType('AMMLTrajectory', (typemap['AMMLTrajectory'],), {})
ChemReaction = DType('ChemReaction', (typemap['ChemReaction'],), {})
ChemSpecies = DType('ChemSpecies', (typemap['ChemSpecies'],), {})

specs = [  # every dict may contain either "basetype" or "ref" key
    {'typ': 'Tuple', 'ref': Tuple},
    {'typ': 'Table', 'ref': Table},
    {'typ': 'Dict', 'ref': Dict},
    {'typ': 'AMMLStructure', 'ref': AMMLStructure},
    {'typ': 'AMMLCalculator', 'ref': AMMLCalculator},
    {'typ': 'AMMLAlgorithm', 'ref': AMMLAlgorithm},
    {'typ': 'AMMLProperty', 'ref': AMMLProperty},
    {'typ': 'AMMLConstraint', 'ref': AMMLConstraint},
    {'typ': 'AMMLTrajectory', 'ref': AMMLTrajectory},
    {'typ': 'ChemReaction', 'ref': ChemReaction},
    {'typ': 'ChemSpecies', 'ref': ChemSpecies},
    {'typ': 'AMMLStructure', 'id': 'name', 'basetype': typemap['String']},
    {'typ': 'AMMLStructure', 'id': 'atoms', 'basetype': 'Series', 'datatype': 'Table'},
    {'typ': 'AMMLStructure', 'id': 'pbc', 'basetype': 'Series', 'datatype': 'BoolArray'},
    {'typ': 'AMMLStructure', 'id': 'cell', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLStructure', 'id': 'kinetic_energy', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLStructure', 'id': 'temperature', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLStructure', 'id': 'distance_matrix', 'basetype': 'Series',
     'datatype': 'FloatArray'},
    {'typ': 'AMMLStructure', 'id': 'chemical_formula', 'basetype': 'Series',
     'datatype': typemap['String']},
    {'typ': 'AMMLStructure', 'id': 'number_of_atoms', 'basetype': 'Series',
     'datatype': typemap['Integer']},
    {'typ': 'AMMLStructure', 'id': 'cell_volume', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLStructure', 'id': 'center_of_mass', 'basetype': 'Series',
     'datatype': 'FloatArray'},
    {'typ': 'AMMLStructure', 'id': 'radius_of_gyration', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLStructure', 'id': 'moments_of_inertia', 'basetype': 'Series',
     'datatype': 'FloatArray'},
    {'typ': 'AMMLStructure', 'id': 'angular_momentum', 'basetype': 'Series',
     'datatype': 'FloatArray'},
    {'typ': 'AMMLCalculator', 'id': 'name', 'basetype': typemap['String']},
    {'typ': 'AMMLCalculator', 'id': 'pinning', 'basetype': typemap['String']},
    {'typ': 'AMMLCalculator', 'id': 'version', 'basetype': typemap['String']},
    {'typ': 'AMMLCalculator', 'id': 'task', 'basetype': typemap['String']},
    {'typ': 'AMMLCalculator', 'id': 'parameters', 'basetype': 'Table'},
    {'typ': 'AMMLAlgorithm', 'id': 'name', 'basetype': typemap['String']},
    {'typ': 'AMMLAlgorithm', 'id': 'parameters', 'basetype': 'Table'},
    {'typ': 'AMMLProperty', 'id': 'names', 'basetype': 'Tuple'},
    {'typ': 'AMMLProperty', 'id': 'calculator', 'basetype': 'AMMLCalculator'},
    {'typ': 'AMMLProperty', 'id': 'algorithm', 'basetype': 'AMMLAlgorithm'},
    {'typ': 'AMMLProperty', 'id': 'structure', 'basetype': 'AMMLStructure'},
    {'typ': 'AMMLProperty', 'id': 'output_structure', 'basetype': 'AMMLStructure'},
    {'typ': 'AMMLProperty', 'id': 'rmsd', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'forces', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'dipole', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'hessian', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'vibrational_modes', 'basetype': 'Series',
     'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'vibrational_energies', 'basetype': 'Series',
     'datatype': 'FloatSeries'},
    {'typ': 'AMMLProperty', 'id': 'energy_minimum', 'basetype': 'Series',
     'datatype': typemap['Boolean']},
    {'typ': 'AMMLProperty', 'id': 'transition_state', 'basetype': 'Series',
     'datatype': typemap['Boolean']},
    {'typ': 'AMMLProperty', 'id': 'energy', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'constraints', 'basetype': 'Tuple'},
    {'typ': 'AMMLProperty', 'id': 'results', 'basetype': 'Table'},
    {'typ': 'AMMLProperty', 'id': 'rdf', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'rdf_distance', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'trajectory', 'basetype': 'Series',
     'datatype': 'AMMLTrajectory'},
    {'typ': 'AMMLProperty', 'id': 'stress', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'magmom', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'magmoms', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'minimum_energy', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'bulk_modulus', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'optimal_volume', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'eos_volume', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'eos_energy', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'dos_energy', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'dos', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'band_structure', 'basetype': 'Series', 'datatype': 'Table'},
    {'typ': 'AMMLProperty', 'id': 'activation_energy', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'reaction_energy', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'maximum_force', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'AMMLProperty', 'id': 'velocity', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'vdf', 'basetype': 'Series', 'datatype': 'FloatArray'},
    {'typ': 'AMMLProperty', 'id': 'neighbors', 'basetype': 'Series', 'datatype': 'Tuple'},
    {'typ': 'AMMLProperty', 'id': 'neighbor_offsets', 'basetype': 'Series', 'datatype': 'Tuple'},
    {'typ': 'AMMLProperty', 'id': 'connectivity_matrix', 'basetype': 'Series',
     'datatype': 'IntArray'},
    {'typ': 'AMMLProperty', 'id': 'connected_components', 'basetype': 'Series',
     'datatype': 'IntArray'},
    {'typ': 'AMMLTrajectory', 'id': 'description', 'basetype': 'Table'},
    {'typ': 'AMMLTrajectory', 'id': 'structure', 'basetype': 'AMMLStructure'},
    {'typ': 'AMMLTrajectory', 'id': 'properties', 'basetype': 'Table'},
    {'typ': 'AMMLTrajectory', 'id': 'constraints', 'basetype': 'Series', 'datatype': 'Tuple'},
    {'typ': 'AMMLTrajectory', 'id': 'filename', 'basetype': typemap['String']},
    {'typ': 'ChemSpecies', 'id': 'properties', 'basetype': 'Table'},
    {'typ': 'ChemSpecies', 'id': 'energy', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemSpecies', 'id': 'enthalpy', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemSpecies', 'id': 'entropy', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemSpecies', 'id': 'free_energy', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'ChemSpecies', 'id': 'zpe', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemSpecies', 'id': 'temperature', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'ChemSpecies', 'id': 'name', 'basetype': typemap['String']},
    {'typ': 'ChemSpecies', 'id': 'composition', 'basetype': typemap['String']},
    {'typ': 'ChemReaction', 'id': 'properties', 'basetype': 'Table'},
    {'typ': 'ChemReaction', 'id': 'energy', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemReaction', 'id': 'enthalpy', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemReaction', 'id': 'entropy', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemReaction', 'id': 'free_energy', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'ChemReaction', 'id': 'zpe', 'basetype': 'Series', 'datatype': typemap['Float']},
    {'typ': 'ChemReaction', 'id': 'temperature', 'basetype': 'Series',
     'datatype': typemap['Float']},
    {'typ': 'Quantity', 'datatype': typemap['Numeric'], 'ref': NumericQuantity},
    {'typ': 'Quantity', 'datatype': typemap['Integer'], 'ref': IntQuantity},
    {'typ': 'Quantity', 'datatype': typemap['Float'], 'ref': FloatQuantity},
    {'typ': 'Quantity', 'datatype': typemap['Complex'], 'ref': ComplexQuantity},
    {'typ': 'Quantity', 'datatype': typemap['Any'], 'ref': AnyQuantity},
    {'typ': 'Series', 'datatype': typemap['Any'], 'ref': AnySeries},
    {'typ': 'Series', 'datatype': typemap['String'], 'ref': StrSeries},
    {'typ': 'Series', 'datatype': typemap['Boolean'], 'ref': BoolSeries},
    {'typ': 'Series', 'datatype': typemap['Integer'], 'ref': IntSeries},
    {'typ': 'Series', 'datatype': typemap['Float'], 'ref': FloatSeries},
    {'typ': 'Series', 'datatype': typemap['Complex'], 'ref': ComplexSeries},
    {'typ': 'Series', 'datatype': typemap['Numeric'], 'ref': NumericSeries},
    {'typ': 'AnySeries', 'datatype': typemap['Any'], 'ref': AnySeries},
    {'typ': 'StrSeries', 'datatype': typemap['String'], 'ref': StrSeries},
    {'typ': 'BoolSeries', 'datatype': typemap['Boolean'], 'ref': BoolSeries},
    {'typ': 'IntSeries', 'datatype': typemap['Integer'], 'ref': IntSeries},
    {'typ': 'FloatSeries', 'datatype': typemap['Float'], 'ref': FloatSeries},
    {'typ': 'ComplexSeries', 'datatype': typemap['Complex'], 'ref': ComplexSeries},
    {'typ': 'NumericSeries', 'datatype': typemap['Numeric'], 'ref': NumericSeries},
    # workaround for a bug in series_type:
    {'typ': 'Series', 'datatype': typemap['Quantity'], 'ref': QuantitySeries},
    {'typ': 'QuantitySeries', 'datatype': typemap['Quantity'], 'ref': QuantitySeries},
    {'typ': 'Array', 'datatype': typemap['Boolean'], 'ref': BoolArray},
    {'typ': 'Array', 'datatype': typemap['String'], 'ref': StrArray},
    {'typ': 'Array', 'datatype': typemap['Integer'], 'ref': IntArray},
    {'typ': 'Array', 'datatype': typemap['Float'], 'ref': FloatArray},
    {'typ': 'Array', 'datatype': typemap['Complex'], 'ref': ComplexArray},
    {'typ': 'Array', 'datatype': typemap['Numeric'], 'ref': NumArray},
    {'typ': 'BoolArray', 'datatype': typemap['Boolean'], 'ref': BoolArray},
    {'typ': 'StrArray', 'datatype': typemap['String'], 'ref': StrArray},
    {'typ': 'IntArray', 'datatype': typemap['Integer'], 'ref': IntArray},
    {'typ': 'FloatArray', 'datatype': typemap['Float'], 'ref': FloatArray},
    {'typ': 'ComplexArray', 'datatype': typemap['Complex'], 'ref': ComplexArray},
    {'typ': 'IntSubArray', 'datatype': typemap['Integer'], 'ref': IntSubArray},
    {'typ': 'FloatSubArray', 'datatype': typemap['Float'], 'ref': FloatSubArray},
    {'typ': 'ComplexSubArray', 'datatype': typemap['Complex'], 'ref': ComplexSubArray},
]


def get_dtype(typ, id_=None, datatype=None):
    """Perform a search either by id_ or by datatype and return a DType type

    Args:
        typ (str): DType name
        id_ (str): optional name of an attribute of typ
        datatype (type): optional datatype for subtyping typ

    Returns:
        the DType type

    Raises:
        StaticTypeError: when DType cannot be determined
    """
    assert not (id_ and datatype)
    for spec in specs:
        if spec['typ'] == typ:
            if id_ is None and 'ref' in spec:
                if datatype:
                    if spec.get('datatype') is datatype:
                        return spec['ref']
                    continue
                return spec['ref']
            if id_ and spec.get('id') == id_:
                assert 'basetype' in spec
                if isinstance(spec['basetype'], type):
                    return spec['basetype']
                if 'datatype' in spec:
                    if isinstance(spec['datatype'], type):
                        return get_dtype(spec['basetype'], datatype=spec['datatype'])
                    typespec = {'datatype': get_dtype(spec['datatype'])}
                    return DType(spec['basetype'], (typemap[spec['basetype']],), typespec)
                return get_dtype(spec['basetype'])
    if id_:
        raise StaticTypeError(f'could not find DType for type: {typ}, id_: {id_}')
    try:
        return DType(typ, (typemap[typ],), {'datatype': datatype})
    except KeyError as err:
        raise StaticTypeError(f'could not find basetype for type: {typ}') from err


def get_type_from_annotation(typec):
    """get the type from a type annotation"""
    basetype = get_basetype_from_annotation(typec)
    if basetype in (typemap['Any'], typemap['Boolean'], typemap['String']):
        return basetype
    if basetype is numpy.ndarray:
        return get_dtype('Array')  # not covered
    return get_dtype(basetype.__name__)


def get_basetype_from_annotation(typec):
    """get the basetype from a type annotation"""
    if typec is typing.Any:
        return typemap['Any']
    if not isinstance(typec, type):
        raise StaticTypeError(f'type annotation "{typec}" not supported')
    if issubclass(typec, ScalarBoolean):
        return typemap['Boolean']
    if issubclass(typec, ScalarString):
        return typemap['String']
    if issubclass(typec, numpy.ndarray):  # bare arrays of datatype bool or str
        return numpy.ndarray
    if issubclass(typec, (list, tuple)):
        return typemap['Tuple']
    if issubclass(typec, dict):
        return typemap['Dict']
    try:
        return typemap[typec.__name__]
    except KeyError as err:
        raise StaticTypeError(f'could not find basetype for type: {typec}') from err
