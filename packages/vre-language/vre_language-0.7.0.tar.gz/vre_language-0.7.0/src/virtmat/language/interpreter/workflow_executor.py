# pylint: disable=protected-access
"""
Language interpreter for distributed/remote evaluation using workflow
management systems and batch systems.

Variables store outputs of function tasks, therefore a variable is in the root
of every evaluation (-> mapped to a task in the workflow). Grouping tasks to
nodes can be done either via simple mapping line of code -> node, or based on
graph analysis.
"""
import base64
import traceback
import uuid
import sys
from functools import cached_property
import dill
import pandas
from textx import get_children_of_type, get_parent_of_type, get_children, get_model
from textx.exceptions import TextXError
from fireworks import fw_config, Firework, Workflow
from virtmat.language.utilities.firetasks import FunctionTask, ExportDataTask
from virtmat.language.utilities.firetasks import BranchTask, ScatterTask, get_fstr
from virtmat.language.utilities.fireworks import run_fireworks, get_ancestors
from virtmat.language.utilities.fireworks import get_nodes_providing, get_parent_nodes
from virtmat.language.utilities.fireworks import safe_update, get_nodes_info, retrieve_value
from virtmat.language.utilities.fireworks import get_fw_metadata, get_launches
from virtmat.language.utilities.fireworks import get_representative_launch
from virtmat.language.utilities.fireworks import get_cd_descendants
from virtmat.language.utilities.serializable import DATA_SCHEMA_VERSION
from virtmat.language.utilities.serializable import FWDataObject, tag_serialize
from virtmat.language.utilities.textx import isinstance_m, get_identifiers
from virtmat.language.utilities.textx import get_bool_param_properties
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.errors import textxerror_wrap, error_handler
from virtmat.language.utilities.errors import EvaluationError, AncestorEvaluationError
from virtmat.language.utilities.errors import raise_exception, TEXTX_WRAPPED_EXCEPTIONS
from virtmat.language.utilities.errors import ConfigurationError, UpdateError
from virtmat.language.utilities.typemap import typemap
from virtmat.language.utilities.typechecks import checktype_value, checktype_func
from virtmat.language.utilities.types import NC, NA, is_scalar_type
from virtmat.language.utilities.types import is_numeric, is_numeric_type
from virtmat.language.utilities.units import get_units, get_dimensionality
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.compatibility import get_grammar_version
from .instant_executor import program_value, plain_type_value, object_import_value
from .deferred_executor import get_general_reference_func


def get_input_name(par):
    """return the input name and input value of a named object"""
    if isinstance_m(par, ['Variable']):
        return par.name, None
    assert isinstance_m(par, ['ObjectImport'])
    return par.name, FWDataObject.from_obj(par.value)


def get_fws(self):
    """Create one or more Firework objects for one Variable object"""
    logger = get_logger(__name__)
    logger.debug('get_fws: processing variable: %s', self.name)
    assert isinstance(self.func, tuple) and len(self.func) == 2
    self.__fw_name = uuid.uuid4().hex
    name_val = (get_input_name(p) for p in self.func[1])
    spec_inp = {n: v for n, v in name_val if v is not None}
    logger.debug('get_fws: spec_inp: %s', spec_inp)
    inputs = [p.name for p in self.func[1]]
    logger.debug('get_fws: input parameters: %s', inputs)
    spec_rsc = {}
    spec_rsc['_source_code'] = self.source_code
    spec_rsc['_grammar_version'] = get_model(self).grammar_version
    spec_rsc['_data_schema_version'] = DATA_SCHEMA_VERSION
    spec_rsc['_python_version'] = sys.version
    if self.resources is None:
        spec_rsc['_category'] = 'interactive'
        spec_rsc['_fworker'] = get_model(self).worker_name
    else:
        if fw_config.MONGOMOCK_SERVERSTORE_FILE is not None:
            msg = 'cannot add statements for batch evaluation with Mongomock'
            raise ConfigurationError(msg)
        spec_rsc['_category'] = 'batch'
        spec_rsc['_fworker'] = self.resources.worker_name
        spec_rsc['_queueadapter'] = self.resources.qadapter
        spec_rsc['_queueadapter']['job_name'] = self.__fw_name
    if hasattr(self, 'dupefinder'):
        spec_rsc['_dupefinder'] = self.dupefinder
    logger.debug('get_fws: spec_rsc: %s', spec_rsc)
    if hasattr(self, 'nchunks'):
        return self._get_fws_parallel(inputs, spec_rsc)
    if self.non_strict:
        return self._get_non_strict_fws(spec_rsc, spec_inp)
    tsk = FunctionTask(func=get_fstr(self.func[0]), inputs=inputs, outputs=[self.name])
    return [Firework([tsk], spec={**spec_rsc, **spec_inp}, name=self.__fw_name)]


def _get_non_strict_fws(self, spec_rsc, spec_inp):
    """process variables with if expressions with non-strict semantics"""
    if isinstance_m(self.parameter, ('IfFunction', 'IfExpression')):
        return self._get_if_fws(spec_rsc, spec_inp)
    assert isinstance_m(self.parameter, ('Or',))
    return self._get_bool_fws(spec_rsc, spec_inp)


def _get_bool_fws(self, spec_rsc, spec_inp):
    """process variables with boolean expressions with nonstrict semantics"""
    get_logger(__name__).debug('get_bool_fws: variable: %s', self.name)
    model = get_model(self)
    wpar, mode, not_ = get_bool_param_properties(self.parameter)
    if mode == 'strict':
        inputs = [p.name for p in self.func[1]]
        tsk = FunctionTask(func=get_fstr(self.func[0]), inputs=inputs, outputs=[self.name])
        return [Firework([tsk], spec={**spec_rsc, **spec_inp}, name=self.__fw_name)]
    assert mode in ('or', 'and')
    # first firework evaluating the left-most operand
    io_name_12 = uuid.uuid4().hex
    tsk_1 = FunctionTask(func=get_fstr(wpar.operands[0].func[0]),
                         inputs=[p.name for p in wpar.operands[0].func[1]],
                         outputs=[f'__{self.name}_{io_name_12}'])
    fwk_1 = Firework([tsk_1], spec={**spec_rsc, **spec_inp}, name=f'_fw_bool_{io_name_12}')
    # second, detouring firework
    non_strict = []
    for operand in wpar.operands[1:]:
        inputs = [p.name for p in operand.func[1]]
        fw_ids = (get_nodes_providing(model.lpad, model.uuid, i)[0] for i in inputs)
        non_strict.append([get_fstr(operand.func[0]), tuple(zip(inputs, fw_ids))])
    tsk_2 = BranchTask(inputs=[f'__{self.name}_{io_name_12}'],
                       outputs=[f'__{self.name}_value'],
                       spec={**spec_rsc, **spec_inp},
                       non_strict=non_strict,
                       mode=mode)
    spec_2 = {k: v for k, v in spec_rsc.items() if k != '_dupefinder'}
    spec_2['_category'] = 'interactive'
    spec_2['_fworker'] = model.worker_name
    fwk_2 = Firework([tsk_2], spec=spec_2, name='_fw_bool_value')
    # third firework collecting and, if needed, negating the result
    tsk_3 = FunctionTask(func=get_fstr(lambda x: not x if not_ else x),
                         inputs=[f'__{self.name}_value'],
                         outputs=[self.name])
    fwk_3 = Firework([tsk_3], spec=spec_rsc, name=self.__fw_name)
    return [fwk_1, fwk_2, fwk_3]


def _get_if_fws(self, spec_rsc, spec_inp):
    """lazy if function/expression using dynamic workflow branching"""
    get_logger(__name__).debug('get_if_fws: variable: %s', self.name)
    model = get_model(self)
    par = self.parameter
    # first firework evaluating the boolean expression
    tsk_1 = FunctionTask(func=get_fstr(par.expr.func[0]),
                         inputs=[p.name for p in par.expr.func[1]],
                         outputs=[f'__{self.name}_expr'])
    fw_1 = Firework([tsk_1], spec={**spec_rsc, **spec_inp}, name=f'_fw_{self.name}_expr')
    # second firework creating a detour with either the true or the false expression
    inp_t = [p.name for p in par.true_.func[1]]
    inp_f = [p.name for p in par.false_.func[1]]
    fw_ids_t = (get_nodes_providing(model.lpad, model.uuid, n)[0] for n in inp_t)
    fw_ids_f = (get_nodes_providing(model.lpad, model.uuid, n)[0] for n in inp_f)
    non_strict = [[get_fstr(par.true_.func[0]), tuple(zip(inp_t, fw_ids_t))],
                  [get_fstr(par.false_.func[0]), tuple(zip(inp_f, fw_ids_f))]]
    tsk_2 = BranchTask(inputs=[f'__{self.name}_expr'],
                       outputs=[f'__{self.name}_value'],
                       spec={**spec_rsc, **spec_inp},
                       non_strict=non_strict,
                       mode='if')
    spec_2 = {k: v for k, v in spec_rsc.items() if k != '_dupefinder'}
    spec_2['_category'] = 'interactive'
    spec_2['_fworker'] = model.worker_name
    fw_2 = Firework([tsk_2], spec=spec_2, name=f'_fw_{self.name}_branch')
    # third firework collecting the result
    tsk_3 = FunctionTask(func=get_fstr(lambda x: x),
                         inputs=[f'__{self.name}_value'],
                         outputs=[self.name])
    fw_3 = Firework([tsk_3], spec=spec_rsc, name=self.__fw_name)
    return [fw_1, fw_2, fw_3]


def _get_fws_parallel(self, inputs, spec_rsc):
    """parallel Map, Filter and Reduce as parameters of Variable (self)"""
    get_logger(__name__).debug('get_fws_in_parallel: variable: %s', self.name)
    if isinstance_m(self.parameter, ('Map',)):
        split = [p.ref.name for p in self.parameter.params]
    else:
        split = [self.parameter.parameter.ref.name]
    chunk_ids = [f'__{self.name}_chunk_{c}' for c in range(self.nchunks)]
    tsk1 = ScatterTask(func=get_fstr(self.func[0]), inputs=inputs,
                       outputs=chunk_ids, split=split, spec=spec_rsc)
    spec = {k: v for k, v in spec_rsc.items() if k != '_dupefinder'}
    spec['_category'] = 'interactive'
    spec['_fworker'] = get_model(self).worker_name
    fw1 = Firework([tsk1], spec=spec, name=f'_fw_{self.name}_scatter')
    if isinstance_m(self.parameter, ('Map', 'Filter')):
        tsk2 = FunctionTask(func=get_fstr(lambda *x: pandas.concat(x)),
                            inputs=chunk_ids,
                            outputs=[self.name])
        fw2 = Firework([tsk2], spec=spec, name=self.__fw_name)
        return [fw1, fw2]
    assert isinstance_m(self.parameter, ('Reduce',))
    io_name = f'__{self.name}_reduce'

    def get_retfunc():
        if issubclass(self.parameter.parameter.type_, typemap['Series']):
            return lambda *x: pandas.Series(x, name=io_name)
        assert issubclass(self.parameter.parameter.type_, typemap['Table'])
        return lambda *x: pandas.concat(x)
    tsk2 = FunctionTask(func=get_fstr(get_retfunc()),
                        inputs=chunk_ids,
                        outputs=[io_name])
    tsk3 = FunctionTask(func=get_fstr(self.func[0]),
                        inputs=[io_name],
                        outputs=[self.name])
    fw2 = Firework([tsk2], spec=spec, name=f'_fw_{self.name}_reduce')
    fw3 = Firework([tsk3], spec=spec, name=self.__fw_name)
    return [fw1, fw2, fw3]


def get_fw_object_to(self):
    """create a single Firework object for an ObjectTo object"""
    spec = {'_source_code': self.source_code, '_category': 'interactive',
            '_fworker': get_model(self).worker_name,
            '_grammar_version': get_model(self).grammar_version,
            '_data_schema_version': DATA_SCHEMA_VERSION,
            '_python_version': sys.version}
    tsk = ExportDataTask(varname=self.ref.name, filename=self.filename, url=self.url)
    self.__fw_name = uuid.uuid4().hex
    return Firework([tsk], spec=spec, name=self.__fw_name)


@textxerror_wrap
@checktype_value
def variable_value(self):
    """obtain an output value from database: asynchronously and non-blocking"""
    logger = get_logger(__name__)
    logger.debug('variable_value:%s', repr(self))
    model = get_model(self)
    fw_p = {'state': True, 'fw_id': True, 'launches': True, 'archived_launches': True}
    fw_dct = model.lpad.fireworks.find_one({'name': self.__fw_name}, fw_p)
    launch = get_representative_launch(get_launches(model.lpad, fw_dct['launches']))
    if fw_dct['state'] == 'COMPLETED':
        assert launch and launch.state == 'COMPLETED'
        return retrieve_value(model.lpad, launch.launch_id, self.name)
    if fw_dct['state'] == 'FIZZLED':
        assert launch and launch.state == 'FIZZLED'
        assert launch.launch_id == fw_dct['launches'][-1]
        launch_q = {'launch_id': launch.launch_id}
        launch_dct = model.lpad.launches.find_one(launch_q, {'action': True})
        if '_exception' in launch_dct['action']['stored_data']:
            logger.error('variable_value:%s evaluation error', repr(self))
            exception_dct = launch_dct['action']['stored_data']['_exception']
            trace = exception_dct['_stacktrace']
            if exception_dct.get('_details') is None:  # not covered
                raise EvaluationError(f'No details found. Stacktrace:\n{trace}')
            pkl = exception_dct['_details']['pkl']
            exc = dill.loads(base64.b64decode(pkl.encode()))
            if isinstance(exc, TEXTX_WRAPPED_EXCEPTIONS):
                raise exc
            lst = traceback.format_exception(type(exc), exc, exc.__traceback__)  # not covered
            raise EvaluationError(''.join(lst)) from exc
        raise EvaluationError('state FIZZLED but no exception found')  # not covered
    if fw_dct['state'] == 'WAITING':
        fw_q = {'fw_id': {'$in': get_ancestors(model.lpad, fw_dct['fw_id'])}, 'state': 'FIZZLED'}
        fizzled = list(model.lpad.fireworks.find(fw_q, projection={'name': True}))
        if fizzled:
            msg = f'Evaluation of {self.name} not possible due to failed ancestors: '
            var_names = []
            vars_ = get_children_of_type('Variable', model)
            for fwk in fizzled:
                try:
                    var_name = next(v.name for v in vars_ if v.__fw_name == fwk['name'])
                except StopIteration:
                    var_name = fwk['name']
                var_names.append(var_name)
            msg += ', '.join(var_names)
            logger.error('variable_value:%s ancestor error', repr(self))
            raise AncestorEvaluationError(msg)
        return NC
    if fw_dct['state'] in ['READY', 'RESERVED', 'RUNNING', 'PAUSED', 'DEFUSED']:
        return NC
    assert fw_dct['state'] == 'ARCHIVED'
    launch = get_representative_launch(get_launches(model.lpad, fw_dct['archived_launches']))
    if launch and launch.state == 'COMPLETED':
        return retrieve_value(model.lpad, launch.launch_id, self.name)
    return NC


@checktype_value
def info_value(self):
    """evaluate the info function object"""
    par = self.param
    name = par.ref.name if isinstance_m(par, ['GeneralReference']) else None
    dct = {'name': name, 'type': par.type_, 'scalar': is_scalar_type(par.type_),
           'numeric': is_numeric_type(par.type_), 'datatype': getattr(par.type_, 'datatype', None)}
    if (isinstance_m(par, ['GeneralReference']) and isinstance_m(par.ref, ['ObjectImport'])
       and callable(par.ref.value)):
        return pandas.DataFrame([dct])
    try:
        parval = par.value
    except TextXError as err:
        dct['error message'] = str(err.__cause__)
        dct['error type'] = type(err.__cause__).__name__
    else:
        if is_numeric(parval) and isinstance(parval, (typemap['Series'], typemap['Quantity'])):
            dct['dimensionality'] = str(get_dimensionality(parval))
            dct['units'] = str(get_units(parval))
    if (isinstance_m(par, ['GeneralReference'])
       and not isinstance_m(par.ref, ['ObjectImport'])):
        model = get_model(self)
        var_list = get_children_of_type('Variable', model)
        var = next(v for v in var_list if v.name == par.ref.name)
        dct.update(get_fw_metadata(model.lpad, {'metadata.uuid': model.uuid},
                                   {'name': var.__fw_name}))
    return pandas.DataFrame([dct])


@textxerror_wrap
@checktype_value
def func_value(self):
    """evaluate a python function object"""
    get_logger(__name__).debug('func_value:%s', repr(self))
    func, pars = self.func
    assert all(isinstance_m(p, ['Variable', 'ObjectImport']) for p in pars)
    return func(*[p.value for p in pars])


@textxerror_wrap
@checktype_value
def func_non_cached_value(self):
    """evaluate a python function object"""
    get_logger(__name__).debug('func_non_cached_value:%s', repr(self))
    func, pars = self.func
    assert all(isinstance_m(p, ['Variable', 'ObjectImport']) for p in pars)
    return func(*[p.non_cached_value for p in pars])


def get_lpad(self):
    """return launchpad object associated with the model"""
    return self._tx_model_params['model_instance']['lpad']


def get_uuid(self):
    """return workflow uuid associated with the model"""
    input_uuid = self._tx_model_params['model_instance']['uuid']
    return uuid.uuid4().hex if input_uuid is None else input_uuid


def get_g_uuid(self):
    """return group uuid of the model"""
    g_uuid = self._tx_model_params['model_instance'].get('g_uuid')
    assert self._tx_model_params['model_instance']['uuid'] is None
    if g_uuid is None:
        return uuid.uuid4().hex
    return g_uuid


def get_list_of_names(self):
    """return a list of the names of all named objects"""
    return [obj.name for obj in get_identifiers(self)]


def get_my_grammar_version(self):
    """get grammar version from grammar string"""
    if self._tx_model_params.get('grammar_str') is not None:
        return get_grammar_version(self._tx_model_params.get('grammar_str'))
    return None


def general_reference_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    def checkref(obj):
        if isinstance_m(obj, ['Variable', 'ObjectImport']):
            return lambda x: x, (obj,)
        return obj.func
    func, pars = checkref(self.ref)
    for accessor in self.accessors:
        func, pars = get_general_reference_func(func, pars, accessor)
    return func, pars


def add_workflow_properties(metamodel):
    """Add class properties using monkey style patching"""
    metamodel['Program'].lpad = property(get_lpad)
    metamodel['Program'].uuid = cached_property(get_uuid)
    metamodel['Program'].uuid.__set_name__(metamodel['Program'], 'uuid')
    metamodel['Program'].g_uuid = cached_property(get_g_uuid)
    metamodel['Program'].g_uuid.__set_name__(metamodel['Program'], 'g_uuid')
    metamodel['Program'].name_list = cached_property(get_list_of_names)
    metamodel['Program'].name_list.__set_name__(metamodel['Program'], 'name_list')
    metamodel['Program'].grammar_version = cached_property(get_my_grammar_version)
    metamodel['Program'].grammar_version.__set_name__(metamodel['Program'], 'grammar_version')
    metamodel['Variable'].fireworks = cached_property(get_fws)
    metamodel['Variable'].fireworks.__set_name__(metamodel['Variable'], 'firework')
    metamodel['Variable'].func = cached_property(checktype_func(lambda x: x.parameter.func))
    metamodel['Variable'].func.__set_name__(metamodel['Variable'], 'func')
    metamodel['Variable']._get_fws_parallel = _get_fws_parallel
    metamodel['Variable']._get_non_strict_fws = _get_non_strict_fws
    metamodel['Variable']._get_if_fws = _get_if_fws
    metamodel['Variable']._get_bool_fws = _get_bool_fws
    metamodel['ObjectTo'].firework = cached_property(get_fw_object_to)
    metamodel['ObjectTo'].firework.__set_name__(metamodel['ObjectTo'], 'firework')
    metamodel['GeneralReference'].func = cached_property(general_reference_func)
    metamodel['GeneralReference'].func.__set_name__(metamodel['GeneralReference'], 'func')
    metamodel['Type'].func = property(lambda x: (lambda: x.value, tuple()))
    mapping_dict = {
        'Program': program_value,
        'Print': error_handler(func_value),
        'Type': info_value,
        'Variable': variable_value,
        'Tag': func_value,
        'Dict': func_value,
        'GeneralReference': func_value,
        'FunctionCall': func_value,
        'IfFunction': func_value,
        'IfExpression': func_value,
        'Expression': func_value,
        'Or': func_value,
        'And': func_value,
        'Not': func_value,
        'Comparison': func_value,
        'Series': func_value,
        'Table': func_value,
        'Tuple': func_value,
        'IterableProperty': func_value,
        'IterableQuery': func_value,
        'ObjectImport': object_import_value,
        'Quantity': func_value,
        'String': textxerror_wrap(checktype_value(plain_type_value)),
        'Bool': textxerror_wrap(checktype_value(plain_type_value)),
        'PrintParameter': func_value,
        'BoolArray': func_value,
        'StrArray': func_value,
        'IntArray': func_value,
        'FloatArray': func_value,
        'ComplexArray': func_value,
        'IntSubArray': func_value,
        'FloatSubArray': func_value,
        'ComplexSubArray': func_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].value = cached_property(func)
        metamodel[key].value.__set_name__(metamodel[key], 'value')
    mapping_dict = {
        'Variable': variable_value,
        'ObjectImport': object_import_value,
        'String': textxerror_wrap(checktype_value(plain_type_value)),
        'Bool': textxerror_wrap(checktype_value(plain_type_value)),
        'Dict': func_non_cached_value,
        'GeneralReference': func_non_cached_value,
        'FunctionCall': func_non_cached_value,
        'IfFunction': func_non_cached_value,
        'IfExpression': func_non_cached_value,
        'Expression': func_non_cached_value,
        'Or': func_non_cached_value,
        'And': func_non_cached_value,
        'Not': func_non_cached_value,
        'Comparison': func_non_cached_value,
        'Series': func_non_cached_value,
        'Table': func_non_cached_value,
        'Tuple': func_non_cached_value,
        'IterableProperty': func_non_cached_value,
        'IterableQuery': func_non_cached_value,
        'Quantity': func_non_cached_value,
        'PrintParameter': func_non_cached_value,
        'BoolArray': func_non_cached_value,
        'StrArray': func_non_cached_value,
        'IntArray': func_non_cached_value,
        'FloatArray': func_non_cached_value,
        'ComplexArray': func_non_cached_value,
        'IntSubArray': func_non_cached_value,
        'FloatSubArray': func_non_cached_value,
        'ComplexSubArray': func_non_cached_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].non_cached_value = property(func)


def add_workflow(model, var_set):
    """create a workflow object from a new model and add it to the database"""
    model_params = getattr(model, '_tx_model_params')
    assert model_params['model_instance']['uuid'] is None
    assert getattr(model, '_wfl_map', None) is None

    fws = []
    for var in var_set:
        fws.extend(var.fireworks)
    outs = {}
    for fwk in fws:
        lst = []
        for task in fwk.tasks:
            if 'outputs' in task:
                lst += task['outputs']
        outs[str(fwk.fw_id)] = lst
    inps = {str(f.fw_id): [i for t in f.tasks for i in t['inputs']] for f in fws}
    links = {}
    # naive implementation of the join
    for ofw in fws:
        oid = ofw.fw_id
        if len(outs[str(oid)]) > 0:
            links[str(oid)] = []
            for ifw in fws:
                for inp in inps[str(ifw.fw_id)]:
                    if inp in outs[str(oid)]:
                        links[str(oid)].append(ifw.fw_id)
    # find all root nodes
    root_fws = []
    for firework in fws:
        if all('inputs' in t and len(t['inputs']) == 0 for t in firework.tasks):
            root_fws.append(firework.fw_id)

    # create a meta node for things like function definitions, imports, etc.
    meta_tasks = [FunctionTask(func=get_fstr(lambda: None), inputs=[], outputs=[])]

    meta_src = []
    for statement in ['ObjectImports', 'FunctionDefinition']:
        for obj in get_children_of_type(statement, model):
            meta_src.extend(obj.source_code)
    root_spec = {'_python_version': sys.version,
                 '_category': 'interactive', '_fworker': model.worker_name}
    meta_spec = {'_python_version': sys.version, '_source_code': meta_src,
                 '_grammar_version': model.grammar_version,
                 '_data_schema_version': DATA_SCHEMA_VERSION}
    meta_spec.update(root_spec)
    tag_dct = {}
    for tag in get_children_of_type('Tag', model):
        tag_dct.update(tag_serialize(tag.value))
    meta_spec['_tag'] = tag_dct

    meta_node = Firework(meta_tasks, name='_fw_meta_node', spec=meta_spec)
    fws.append(meta_node)
    root_fws.append(meta_node.fw_id)

    # create a new empty root node
    root_node = Firework(meta_tasks, name='_fw_root_node', spec=root_spec)
    fws.append(root_node)

    # link all root nodes to the new root node
    links[str(root_node.fw_id)] = root_fws
    metadata = {'uuid': model.uuid, 'g_uuid': model.g_uuid,
                'grammar_str': model_params.get('grammar_str'),
                'data_schema_version': DATA_SCHEMA_VERSION}
    name = 'Created by textS/textM interpreter'
    wfl = Workflow(fws, links_dict=links, metadata=metadata, name=name)
    setattr(model, '_wfl_map', model.lpad.add_wf(wfl))


def append_var_nodes(model, var_set):
    """append Variable nodes to workflow after resolving their dependencies"""
    logger = get_logger(__name__)
    logger.debug('append_var_nodes: total number of variables: %s', len(var_set))
    nodes = []
    vars_ = []
    for var in var_set:
        fw_ids = get_nodes_providing(model.lpad, model.uuid, var.name)
        if len(fw_ids) != 0:
            assert len(fw_ids) == 1
            if getattr(var, '_update', None):
                cd_desc = get_cd_descendants(model.lpad, model.uuid, fw_ids[0])
                if cd_desc:
                    msg = (f'Variable \"{var.name}\" cannot be updated due to '
                           f'{len(cd_desc)} completed detouring descendants.')
                    logger.error('append_var_nodes: %s', msg)
                    raise_exception(var, UpdateError, msg)
                logger.debug('append_var_nodes: updating variable: %s', var.name)
                assert len(var.fireworks) == 1
                fwk = var.fireworks[0].to_dict()
                logger.debug('updating spec: %s', fwk['spec'])
                safe_update(model.lpad, fw_ids[0], fwk['spec'])
            fwk = model.lpad.fireworks.find_one({'fw_id': fw_ids[0]}, {'name': True})
            var.__fw_name = fwk['name']
            msg = 'append_var_nodes: persistent variable: %s, fw_name: %s'
            logger.debug(msg, var.name, fwk['name'])
        else:
            nodes.extend(var.fireworks)
            vars_.extend(var.name)
    nodes_len = len(nodes)
    logger.debug('append_var_nodes: appending %s new variables: %s', nodes_len, vars_)
    while nodes:
        num_nodes = len(nodes)
        for ind, (node, var) in enumerate(zip(nodes, vars_)):
            msg = 'append_var_nodes: trying to append variable: %s, node: %s'
            get_logger(__name__).debug(msg, var, node.fw_id)
            parents = get_parent_nodes(model.lpad, model.uuid, node)
            if None not in parents:
                msg = 'append_var_nodes: appending variable: %s, node: %s, parents: %s'
                get_logger(__name__).debug(msg, var, node.fw_id, parents)
                model.lpad.append_wf(Workflow([nodes.pop(ind)]), fw_ids=parents)
                break
        assert len(nodes) < num_nodes
    logger.debug('appended %s new variable nodes', nodes_len)


def append_output_nodes(model):
    """check ObjectTo objects and append ObjectTo nodes to workflow"""
    logger = get_logger(__name__)
    for obj_to in get_children_of_type('ObjectTo', model):
        wf_query = {'metadata.uuid': model.uuid}
        fw_query = {'spec._tasks.0.varname': obj_to.ref.name,
                    'spec._tasks.0.filename': obj_to.filename,
                    'spec._tasks.0.url': obj_to.url}
        fw_proj = {'name': True}
        wfs = get_nodes_info(model.lpad, wf_query, fw_query, fw_proj)
        nodes = next(wf['nodes'] for wf in wfs)
        if nodes:
            assert len(nodes) == 1
            obj_to.__fw_name = next(n['name'] for n in nodes)
        else:
            parents = get_nodes_providing(model.lpad, model.uuid, obj_to.ref.name)
            model.lpad.append_wf(Workflow([obj_to.firework]), fw_ids=parents)
            logger.debug('added output node for var %s', obj_to.ref.name)


@textxerror_wrap
def update_tag(tag, tag_dct):
    """update model tag"""
    tag_dct.update(tag_serialize(tag.value))


def update_meta_node(model):
    """update the meta node with tags, object imports and function definitions"""
    meta_src = []
    for statement in ['ObjectImports', 'FunctionDefinition']:
        for obj in get_children_of_type(statement, model):
            meta_src.extend(obj.source_code)
    wf_q = {'metadata.uuid': model.uuid}
    fw_q = {'name': '_fw_meta_node'}
    fw_p = {'spec': True, 'fw_id': True}
    wfs = get_nodes_info(model.lpad, wf_q, fw_q, fw_p)
    assert len(wfs) == 1
    assert len(wfs[0]['nodes']) == 1
    fwk = wfs[0]['nodes'][0]
    if sorted(fwk['spec']['_source_code']) != sorted(meta_src):
        safe_update(model.lpad, fwk['fw_id'], {'_source_code': meta_src})
        get_logger(__name__).info('updated meta node %s: _source_code: %s',
                                  fwk['fw_id'], meta_src)
    tags = get_children_of_type('Tag', model)
    if tags:
        tag_dct = fwk['spec'].get('_tag') or {}
        for tag in tags:
            update_tag(tag, tag_dct)
        safe_update(model.lpad, fwk['fw_id'], {'_tag': tag_dct})
        get_logger(__name__).info('updated meta node %s: _tag: %s', fwk['fw_id'],
                                  formatter(tag_dct))


def get_if_nonstrict(obj):
    """get a set of non-strict parameters of IF function/expression"""
    obj_expr_value = obj.expr.non_cached_value
    if obj_expr_value is NC or obj_expr_value is NA:
        return set(obj.true_.func[1]) | set(obj.false_.func[1])
    if obj_expr_value:
        return set(obj.false_.func[1])
    return set(obj.true_.func[1])


def get_bool_nonstrict(obj, op):
    """get a set of non-strict parameters of boolean operators OR/AND"""
    assert op in ('Or', 'And')
    operands = list(obj.operands)
    while operands:
        operand = operands.pop(0)
        operand_value = operand.non_cached_value
        if operand_value is NA:
            if op == 'And':
                return set().union(*(op.func[1] for op in operands))
            continue
        need_val = operand_value if op == 'Or' else not operand_value
        if operand_value is NC or need_val:
            return set().union(*(op.func[1] for op in operands))
    return set()


def get_nonstrict(model):
    """return globally non-strict variables"""
    refs = get_children_of_type('GeneralReference', model)
    refs = [r for r in refs if isinstance_m(r.ref, ('Variable',))]
    refs = [r for r in refs if not get_parent_of_type('IfFunction', r)]
    refs = [r for r in refs if not get_parent_of_type('IfExpression', r)]
    refs = [r for r in refs if not get_parent_of_type('Or', r)]
    refs = [r for r in refs if not get_parent_of_type('And', r)]

    non_strict = set()
    for obj in get_children(lambda x: isinstance_m(x, ('IfFunction', 'IfExpression')), model):
        non_strict.update(get_if_nonstrict(obj))
    for op in ('And', 'Or'):
        for obj in get_children_of_type(op, model):
            non_strict.update(get_bool_nonstrict(obj, op))
    non_strict -= set(r.ref for r in refs)
    get_logger(__name__).debug('non-strict vars: %s', non_strict)
    return non_strict


def get_fw_ids_torun(model):
    """return the list of nodes for which evaluation has been requested"""
    vars_ = set()

    def select_vars(x):
        return (isinstance_m(x, ['GeneralReference'])
                and isinstance_m(x.ref, ['Variable'])
                and not get_parent_of_type('Type', x))
    for prnt in get_children(lambda x: isinstance_m(x, ('Print', 'View')), model):
        vars_.update(vref.ref for vref in get_children(select_vars, prnt))
    vars_ -= get_nonstrict(model)
    fw_ids = []
    for var in iter(vars_):
        fw_ids.extend(model.lpad.get_fw_ids({'name': var.__fw_name}))
    anc_ids = [a for i in fw_ids for a in get_ancestors(model.lpad, i)]
    return list(set(fw_ids+anc_ids))


def get_var_batches(model):
    """split the set of variables into a list of sets based on their dependencies"""
    logger = get_logger(__name__)
    vars_ = set(get_children_of_type('Variable', model))
    logger.debug('get_var_batches: variables: %s', vars_)
    nvars = len(vars_)

    def get_parent_vars(var):
        refs = get_children_of_type('GeneralReference', var)
        pvars = {r.ref for r in refs if isinstance_m(r.ref, ('Variable',))}
        pvars.update([v2 for v1 in pvars for v2 in get_parent_vars(v1)])
        return pvars

    ancestors = {var.name: get_parent_vars(var) for var in vars_}
    logger.debug('get_var_batches: ancestors: %s', ancestors)

    vars_ns = {var for var in vars_ if var.non_strict}
    logger.debug('get_var_batches: vars with non-strict semantics: %s', vars_ns)
    nvars_ns = len(vars_ns)

    batches = []
    while vars_ns:
        for var in vars_ns:
            if all(v not in ancestors[var.name] for v in vars_ns):
                new = set(ancestors[var.name])
                for batch in batches:
                    new -= batch
                if new:
                    batches.append(new)
                batches.append(set([var]))
                vars_ns.remove(var)
                vars_.remove(var)
                vars_ -= new
                break
    if vars_:
        batches.append(vars_)
    assert nvars == sum(len(b) for b in batches)
    if nvars and not nvars_ns:
        assert len(batches) == 1
    logger.debug('get_var_batches: batches of variables: %s', batches)
    return batches


def workflow_model_processor(model, _):
    """generate a workflow for the just created model"""
    logger = get_logger(__name__)
    if not isinstance(model, str):
        batches = get_var_batches(model)
        model_params = getattr(model, '_tx_model_params')
        if model_params['model_instance']['uuid'] is None:
            logger.info('creating model from scratch')
            add_workflow(model, batches[0] if batches else [])
            for batch in batches[1:]:
                append_var_nodes(model, batch)
            append_output_nodes(model)
            logger.info('created model with UUID %s', model.uuid)
        else:
            logger.info('extending model with UUID %s', model.uuid)
            for batch in batches:
                append_var_nodes(model, batch)
            append_output_nodes(model)
            update_meta_node(model)
            logger.info('extended model with UUID %s', model.uuid)
        if model_params.get('autorun'):
            logger.info('running model with UUID %s', model.uuid)
            logger.info('evaluation on-demand: %s', model_params.get('on_demand'))

            def get_fws_torun():
                """return a list of fireworks if there are READY fireworks"""
                fw_q = {'state': 'READY', 'spec._category': 'interactive'}
                if model_params.get('on_demand'):
                    fw_q.update({'fw_id': {'$in': get_fw_ids_torun(model)}})
                    return model.lpad.get_fw_ids(fw_q)
                wf_q = {'metadata.uuid': model.uuid}
                return model.lpad.get_fw_ids_in_wfs(wf_q, fw_q)

            unique_launchdir = model_params.get('unique_launchdir', False)
            fws_to_run = get_fws_torun()
            while fws_to_run:
                run_fireworks(model.lpad, fws_to_run, worker_name=model.worker_name,
                              create_subdirs=unique_launchdir)
                fws_to_run = get_fws_torun()
    else:
        logger.info('empty model')
