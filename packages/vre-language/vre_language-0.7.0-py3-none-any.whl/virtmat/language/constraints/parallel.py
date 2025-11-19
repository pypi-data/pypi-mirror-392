"""apply constraints for parallelizable objects"""
from textx import get_children_of_type, get_parent_of_type, textx_isinstance
from virtmat.language.utilities.textx import is_reference
from virtmat.language.utilities.errors import raise_exception, ParallelizationError


def check_parallelizable_processor(model, metamodel):
    """
    Apply constraints to parallelizable (Map, Filter and Reduce) objects and
    add attributes to their parent Variable objects
    """
    for cls in ['Map', 'Filter', 'Reduce']:  # classes with nchunks attribute
        for obj in get_children_of_type(cls, model):
            if obj.nchunks is not None:
                parent = get_parent_of_type('Variable', obj)
                if parent is None or parent.parameter is not obj:
                    msg = 'Parallel map, filter and reduce must be variable parameters'
                    raise_exception(obj, ParallelizationError, msg)
                if textx_isinstance(obj, metamodel['Map']):
                    if not all(is_reference(p, metamodel) for p in obj.params):
                        msg = 'All parallel map parameters must be references'
                        raise_exception(obj, ParallelizationError, msg)
                else:  # Filter or Reduce
                    if not is_reference(obj.parameter, metamodel):
                        msg = 'Parallel filter/reduce parameter must be a reference'
                        raise_exception(obj, ParallelizationError, msg)
                setattr(parent, 'nchunks', obj.nchunks)
