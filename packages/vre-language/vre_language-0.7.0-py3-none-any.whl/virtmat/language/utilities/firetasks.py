"""custom firetasks for use in the interpreter"""
import os
import base64
import uuid
import contextlib
import dill
import pandas
import numpy
from fireworks import Workflow, Firework, FWAction, FireTaskBase, explicit_serialize
from virtmat.language.utilities.serializable import FWDataObject
from virtmat.language.utilities.errors import CompatibilityError, ParallelizationError
from virtmat.language.utilities.types import NA


def get_fstr(func):
    """Return a pickle-serialized function as a Python3 string"""
    return base64.b64encode(dill.dumps(func)).decode('utf-8')


def get_exception_serializable(exc):
    """make an exception fireworks-serializable
    https://materialsproject.github.io/fireworks/failures_tutorial.html
    """
    cls = exc.__class__
    dct = {'name': cls.__name__, 'module': cls.__module__, 'msg': str(exc),
           'pkl': base64.b64encode(dill.dumps(exc)).decode('utf-8')}
    exc.to_dict = lambda: dct
    return exc


@contextlib.contextmanager
def setenv(varname, value):
    """set or change an environment variable temporarily"""
    var_bck = os.environ.get(varname)
    os.environ[varname] = str(value)
    try:
        yield
    finally:
        if var_bck is None:
            del os.environ[varname]
        else:
            os.environ[varname] = var_bck


class FunctionTask(FireTaskBase):
    """call a pickled function with JSON serializable inputs, return JSON
    serializable outputs"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['func', 'inputs', 'outputs']

    def run_task(self, fw_spec):
        inputs = self.get('inputs', [])
        assert isinstance(inputs, list)
        assert all(isinstance(fw_spec[i], FWDataObject) for i in inputs)
        try:
            params = [fw_spec[i].value for i in inputs]
            func = dill.loads(base64.b64decode(self['func'].encode()))
            with setenv('WORKFLOW_EVALUATION_MODE', 'yes'):
                f_output = func(*params)
        except SystemError as err:
            if 'unknown opcode' in str(err):
                python = fw_spec.get('_python_version') or 'unknown'
                msg = (f'This statement has been compiled with incompatible python '
                       f'version: {python}.\nEither rerun and use the same version'
                       f' or use variable update ":=" to re-compile the statement.')
                raise get_exception_serializable(CompatibilityError(msg)) from err
            raise get_exception_serializable(err) from err  # not covered
        except BaseException as err:
            raise get_exception_serializable(err) from err
        return self.get_fw_action(f_output)

    def get_fw_action(self, output):
        """construct a FWAction object from the output of a function"""
        outputs = self.get('outputs', [])
        assert isinstance(outputs, list)
        assert all(isinstance(o, str) for o in outputs)
        if len(outputs) == 1:
            update_dct = {outputs[0]: FWDataObject.from_obj(output)}
            return FWAction(update_spec=update_dct)
        assert len(outputs) == 0 and output is None
        return FWAction()


class ExportDataTask(FireTaskBase):
    """export specified data to a file or url"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['varname']
    optional_params = ['filename', 'url']

    def run_task(self, fw_spec):
        datastore = {'type': 'file'} if self.get('filename') else {'type': 'url'}
        data_obj = fw_spec[self.get('varname')]
        data_obj.offload_data(datastore=datastore, url=self.get('url'),
                              filename=self.get('filename'))
        return FWAction()


@explicit_serialize
class BranchTask(FireTaskBase):
    """implement branching function as a dynamic sub-workflow"""
    required_params = ['inputs', 'non_strict', 'outputs', 'spec', 'mode']

    def run_task(self, fw_spec):
        assert self['mode'] in ('if', 'or', 'and')
        assert isinstance(fw_spec[self['inputs'][0]], FWDataObject)
        expr_val = fw_spec[self['inputs'][0]].value

        if self['mode'] == 'if':
            return self.run_if_task(expr_val)
        return self.run_bool_task(expr_val)

    def run_if_task(self, expr_val):
        """specialize branch task for if expression/function"""
        if expr_val is NA:
            update_dct = {self['outputs'][0]: FWDataObject.from_obj(NA)}
            return FWAction(update_spec=update_dct)
        func = self['non_strict'][0][0] if expr_val else self['non_strict'][1][0]
        pars = self['non_strict'][0][1] if expr_val else self['non_strict'][1][1]
        inputs = [p[0] for p in pars]
        fw_ids = [p[1] for p in pars]
        task = FunctionTask(func=func, inputs=inputs, outputs=self['outputs'])
        fwk = Firework(task, spec=self['spec'], name=self['outputs'][0])
        dct = {'detour': True, 'workflow': Workflow(fireworks=[fwk]), 'parents': fw_ids}
        return FWAction(append_wfs=dct)

    def run_bool_task(self, expr_val):
        """specialize branch task for or/and expression"""
        bmode = self['mode'] == 'or'  # bmode is True for 'or', bmode is False for 'and'
        if expr_val is bmode:
            return FWAction(update_spec={self['outputs'][0]: FWDataObject.from_obj(bmode)})
        if len(self['non_strict']) == 0:
            rval = NA if expr_val is NA else not bmode
            return FWAction(update_spec={self['outputs'][0]: FWDataObject.from_obj(rval)})
        func_str = self['non_strict'][0][0]

        def binary_bool_func(*args):
            rval = dill.loads(base64.b64decode(func_str.encode()))(*args)
            if rval is (not bmode):
                return NA if expr_val is NA else not bmode
            return rval
        io_name = uuid.uuid4().hex
        tsk_1 = FunctionTask(func=get_fstr(binary_bool_func),
                             inputs=[p[0] for p in self['non_strict'][0][1]],
                             outputs=[f'_fw_bool_{io_name}'])
        fwk_1 = Firework(tsk_1, spec=self['spec'], name=f'_fw_bool_{io_name}')
        tsk_2 = BranchTask(inputs=[f'_fw_bool_{io_name}'],
                           non_strict=self['non_strict'][1:],
                           spec=self['spec'],
                           outputs=self['outputs'],
                           mode=self['mode'])
        spec_2 = {k: v for k, v in self['spec'].items() if k != '_dupefinder'}
        fwk_2 = Firework([tsk_2], spec=spec_2, name='_fw_bool_value')
        wfl = Workflow([fwk_1, fwk_2], links_dict={str(fwk_1.fw_id): [fwk_2.fw_id]})
        fw_ids = [p[1] for p in self['non_strict'][0][1]]
        return FWAction(append_wfs={'detour': True, 'workflow': wfl, 'parents': fw_ids})


class ScatterTask(FireTaskBase):
    """implement parallelized map function as a dynamic sub-workflow"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['func', 'split', 'inputs', 'outputs', 'spec']

    def run_task(self, fw_spec):
        assert isinstance(self['inputs'], list)
        assert isinstance(self['outputs'], list)
        assert isinstance(self['split'], list)
        assert all(isinstance(i, str) for i in self['inputs'])
        assert all(isinstance(o, str) for o in self['outputs'])
        assert all(isinstance(i, str) for i in self['split'])
        assert len(set((len(fw_spec[i].value) for i in self['split']))) == 1
        nchunks = len(self['outputs'])

        dcts = [self['spec'].copy() for _ in range(nchunks)]
        for inp in self['split']:
            assert isinstance(fw_spec[inp].value, (pandas.Series, pandas.DataFrame))
            if nchunks > len(fw_spec[inp].value):
                msg = (f'number of chunks {nchunks} larger that number of elements'
                       f' {len(fw_spec[inp].value)}')
                raise get_exception_serializable(ParallelizationError(msg))
            chunks = numpy.array_split(fw_spec[inp].value, nchunks)
            for dct, chunk in zip(dcts, chunks):
                dct[inp] = FWDataObject.from_obj(chunk)
        for inp in self['inputs']:
            if inp not in self['split']:
                for dct in dcts:
                    dct[inp] = fw_spec[inp]
        fireworks = []
        for chunk_id, dct in zip(self['outputs'], dcts):
            task = FunctionTask(func=self['func'], inputs=self['inputs'],
                                outputs=[chunk_id])
            fireworks.append(Firework(task, spec=dct, name=chunk_id))
        return FWAction(detours=fireworks)
