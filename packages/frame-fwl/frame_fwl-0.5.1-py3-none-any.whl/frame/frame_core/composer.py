from frame.frame_core.frames import *
from frame.frame_core.plugins import MathPlugin
from frame.frame_core.funcs import has_module
import os, subprocess, time, ast




class FramesComposer:
    '''
# FramesComposer
Fames archestrator. Based by 2 archs: dict (where indexes is any data) and array (where indexes is integrers).

## Args:
- {safemode}: bool - superglobal.safemode state.
- {arch}: str[dict/array (array is VERY experemental)] - arch base.
- {superglobal_name}: str - name of superglobal context.

## Functions:
- [fast_import] - import module to compose.
- [load_fame] - load frame to compose.
- [check_deps] - check dependencies.
- [get_frame] - get frame from compose.
- [sync] - sync data of 2 frames.
- [deploy] - run and deploy compose method.
- [_data] - compile composer to dict.
- [_load_data] - load compiled data to compose from dict.
- [save/load] - serealize methods.
- [from_file] (classmethod) - create compose from file.
- [test_exec] - checks and test run compose.
- [__call__] - return superglobal context.
- [__getitem__] - get frame by name.
- [__setitem__] - load frame by name, format `compose[name] = frame`.
- [__add__] - load frame with format like `compose + frame`.
- [context manager `with` support]
- [else systems]

## Example:
```
with FramesComposer(safemode=False) as fc:
    fc['test1'] = Frame(safemode=False)
    fc['test2'] = Frame(safemode=False)
    @fc['test2'].register()
    def test():
        return 'compleate'
    with fc['test2'] as f:
        f.Var('x', 10)
        f.Var('y', 50)
```
    '''
    def __init__(self, safemode: bool = False, arch: str = 'dict', superglobal_name: str = 'sgc'):
        framer = 'new' 
        self.__safemode = safemode
        save_while_exit = False
        save_args = ['ctx', 'pickle']
        self._superglobal_name = superglobal_name
        self.sgc = Frame(framer, self.__safemode, superglobal_name, save_while_exit, save_args) # superglobal context
        self._frames: list[Frame] | dict[str, Frame] = {} if arch == 'dict' else []
        self._arch = arch
        self._deps = []
        self.__temp_names = []
    def fast_import(self, modulename):
        'fast module import into compose'
        if has_module(modulename): self.sgc.Code(f'import {modulename}')
        else: self.sgc.Code(f'"!WARNING: MODULE CAN BE IS NOT INSTALLED!"\nimport {modulename}')
    def load_frame(self, 
                   index: str | int, 
                   frame: Frame, 
                   add_to_deps: bool = True) -> FramesComposer:
        '''
#### Create frame in composer.
#### Args: 
- {index}: int | str - new frame index.
- {frame}: Frame - frame object to append into composer.
- {add_to_deps}: bool - add frame name to dependencies if true, else pass.
        '''
        self.__temp_names.append(index)
        self._deps.append(index) if add_to_deps else None
        if self._arch == 'dict': self._frames[index] = frame
        else: 
            pre = self._frames[:index-1]
            after = self._frames[index:]
            _frames = pre + [frame] + after
            self._frames = _frames
        return self
    def check_deps(self):
        '''
Check dependencies of composer.
        '''
        for i in self._deps: 
            if i not in self.__temp_names:
                raise FrameComposeError(i, 'FRAME NOT FOUND', f'Dependency is not found: [{i}].')
    def get_frame(self, index: str | int) -> Frame:
        '''
Get frame by {index}.
        '''
        try: return self._frames[int(index) if self._arch == 'array' else index]
        except (IndexError, KeyError) as e: raise FrameComposeError(index, 'GetFrameError', e)
    def sync(self, name_1: str, name_2: str, algoritm: int = 1) -> FramesComposer:
        '''
Sync 2 frames with algoritm.

Algoritms:
    - 1: sync variables
    - 2: algoritm 1 + sync code
        '''
        'algoritms: 1 - async code, 2 - sync code'
        if name_1 not in ('$', 'sgc'):
            f1 = self._frames[name_1]  
        else: f1 =  self.sgc
        if name_2 not in ('$', 'sgc'):
            f2 = self._frames[name_2]
        else: f2 = self.sgc
        new_dict1 = {}
        for i in f1.framer._aliases: 
            new_dict1[i] = f1.framer._aliases[i]
        for i in f2.framer._aliases: 
            new_dict1[i] = f2.framer._aliases[i]
        f1.framer._aliases = new_dict1
        f2.framer._aliases = new_dict1
        new_dict2 = {}
        for i in f1.framer._vars: 
            new_dict2[i] = f1.framer._vars[i]
        for i in f2.framer._vars: 
            new_dict2[i] = f2.framer._vars[i]
        f1.framer._vars = new_dict2
        f2.framer._vars = new_dict2
        if algoritm == 2:
            f1c = f1.framer._code
            f1.framer._code = f1c + f2.framer._code
            f2.framer._code = f2.framer._code + f1c
        if name_1 not in ('$', 'sgc'): self._frames[name_1] = f1
        else: self.sgc = f1
        if name_2 not in ('$', 'sgc'): self._frames[name_2] = f2
        else: self.sgc = f2
        return self
    def superglobal(self) -> Frame: 'get superglobal context of class'; return self.sgc
    def deploy(
        self,
        name: str,
        fcomp_filename: str,
        fcomp_format: str = 'json',
        main_code: str = '',
        runfile_dir: str = os.getcwd(),
        metadata: str = '',
        version: str = None,
        author: str = None,
        dependencies: list = None,
        runing: bool = False
    ):
        '''
# Deploy compose
Method to compile and deploy your compose to file and run (optional).

## Args:
- {name}: str - filename to deployfile.
- {fcomp_filename}: str - fcomp iso dilename.
- {fcomp_format}: str - fcomp format.
- {main_code}: str - deployfile code.
- {runfile_dir}: str - main dir for deployfile.
- {metadata}: str - metadata for deployfile.
    - {version}: str - metadata
    - {author}: str - metadata
- {dependencies}: str - deps for deploy
- {running}: bool - running deploy file if true, else pass

## Example: 
```
with FramesComposer.from_file(filepath, format) as fc: fc.deploy('test.py', 'fc.json', runing=True)
```
This is simple deploy of file.
        '''
        self.check_deps()
        if self.__safemode:
            raise FrameComposeError(f'Superglobal Context [{self._superglobal_name}]', 'EXEC ERROR',
            'FramesCompose deploy is imposible in safemode.')
        imports = ['from frame import *'] + [(f'import {i}' for i in dependencies) if dependencies not in (None, []) else '']
        def metadata_compiler(mtdt):
            mtdt = f'deploy_time = {time.time()}{"\n" if mtdt else ""}' + mtdt
            counter = 1
            max_lines = 3
            new_mtd = ''
            for i in mtdt.split('\n'):
                new_mtd +=  f'    {counter}{" " * (max_lines-len(str(counter)))}| ' + str(i) + '\n'
                counter += 1
            return new_mtd
        metadata = metadata_compiler(metadata)
        done_imports = imports[0]
        for i in imports[1]: done_imports += f'\n{i}'
        code = f'''
"""

==========================================
Deploy file [{name}] for fcomp by [{author}]
Version: {version}
Metadata:
{metadata}
==========================================

"""

# fcirf - frames composotion iso runtime file
_fcirf_version_ = {repr(version)}
_fcirf_name_ = {repr(name)}
_fcirf_author_ = {repr(author)}
_fcirf_dir_ = {repr(runfile_dir)}
_fcirf_deps_ = {dependencies}
_fcirf_fcomp_info_ = {[fcomp_filename, fcomp_format]}

# imports
{done_imports}

fcomp = FramesComposer.from_file(_fcirf_fcomp_info_[0], _fcirf_fcomp_info_[1])
sgc = fcomp.superglobal

{main_code}
        '''
        path = f'{runfile_dir}/{name}'
        with open(path, 'w') as file:
            file.write(code)
        if runing: 
            command = f'python3 {path}'
            os.system(command=command)
        return self
    def _data(self):
        '''Compile composer to dictionary data.'''
        data = {'_frames': {}}
        data['_superglobal_name'] = self._superglobal_name
        data['_arch'] = self._arch
        data['_deps'] = self._deps
        data['__safemode'] = self.__safemode
        data['sgc'] = self.sgc.data
        for i in self._frames.keys(): 
            data['_frames'][i] = self._frames[i].data
        return data
    def _load_data(self, data: dict):
        """Load data into existing FramesComposer instance"""
        self._superglobal_name = data['_superglobal_name']
        self._arch = data['_arch']
        self._deps = data['_deps']
        self.__safemode = data['__safemode']
        # Load superglobal context
        self.sgc._load_data(data['sgc'])
        # Clear current frames
        self._frames = {} if self._arch == 'dict' else []
        # Load all frames
        if isinstance(data['_frames'], dict): fr = data['_frames'].items()
        elif isinstance(data['_frames'], list): fr = data['_frames']
        else:
            raise FrameComposeError('', 'UNKNOWN TYPE TO LOAD', 'Unknown arch for load fcomp file.')
        for frame_name, frame_data in fr:
            frame = Frame()
            frame._load_data(frame_data)
            self.load_frame(frame_name, frame)
    def save(self, filename, format: str = 'json'):
        '''
        ## Saving FramesComposer to file.
        ### Args:
        - {filename}: str - file name
        - {format}: str - saving format ('pickle' or 'json')
        ''' 
        data = self._data()
        try:
            if format == 'pickle':
                with open(filename, 'wb') as f: 
                    pickle.dump(data, f)
            elif format == 'json':
                with open(filename, 'w', encoding='utf-8') as f: 
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else: 
                raise FrameApiError(f"Unsupported format: {format}")
            return self
        except Exception as e:
            raise FrameApiError(f"Save failed: {e}")
    def load(self, filename: str, format: str = 'json') -> 'FramesComposer':
        '''
        ## Loading FramesComposer from file.
        ### Args:
        - {filename}: str - file name  
        - {format}: str - loading format ('pickle' or 'json')
        ### Returns:
        - FramesComposer: self for method chaining
        '''
        try:
            if format == 'pickle':
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
            elif format == 'json':
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                raise FrameApiError(f"Unsupported format: {format}")
            
            self._load_data(data)
            return self
            
        except FileNotFoundError:
            raise FrameApiError(f"File not found: {filename}")
        except Exception as e:
            raise FrameApiError(f"Load failed: {e}")
    @classmethod
    def from_file(cls, filename: str, format: str = 'json') -> 'FramesComposer':
        '''
        ## Create FramesComposer from file (class method)
        ### Args:
        - {filename}: str - file name
        - {format}: str - loading format ('pickle' or 'json')
        ### Returns:
        - FramesComposer: new instance loaded from file
        '''
        composer = cls()
        composer.load(filename, format)
        return composer
    def test_exec(self) -> 'FramesComposer':
        self.check_deps()
        if self.__safemode:
            raise FrameComposeError(f'Superglobal Context [{self._superglobal_name}]', 'EXEC ERROR',
            'Execution is imposible in safemode.')
        self.sgc.Exec()
        return self
    def __enter__(self) -> FramesComposer: return self
    def __exit__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwds) -> Frame: return self.superglobal()
    def __add__(self, other: Frame) -> None: 
        if isinstance(other, Frame): self.load_frame(len(self._frames) if self._arch == 'array' else other._name, other)
        else: raise FrameComposeError('', 'NotSuuportableObject', f"Inncorect attemp to add {type(other)} object to frames.")
    def __getitem__(self, index) -> Frame:
        try: return self._frames[index]
        except (IndexError, KeyError) as e: raise FrameComposeError(index, 'GetFrameError', f'Unknown key: {e}')
        except Exception as e: raise FrameComposeError(index, 'GetItemError', e)
    def __setitem__(self, index, value):
        try: self.load_frame(index, value)
        except (IndexError, KeyError) as e: raise FrameComposeError(index, 'GetFrameError', f'Unknown key: {e}')
        except Exception as e: raise FrameComposeError(index, 'SetItemError', e)
    def __eq__(self, value) -> bool:
        if isinstance(value, FramesComposer): 
            cond1 = value.__safemode == self.__safemode and value._arch == self._arch
            cond2 = value.sgc._name == self.sgc._name  and value._superglobal_name == self._superglobal_name
            return cond1 and cond2
        else: return False
    def __format__(self, format_spec: str) -> str:
        if format_spec == '.all': return str(self._frames)
        elif format_spec.startswith('.get>'):
            index = format_spec[5:]
            list = {}
            counter = 0
            for i in self._frames: 
                list[str(counter)] = self._frames[i]
                counter += 1
            try: return str(list[str(index)])
            except (KeyError) as e: 
                raise FrameComposeError(f'index<{index}>', 'GetItemError', f'Unknown key: {e}')
            except Exception as e: raise FrameComposeError(index, 'fStringError', e)
        elif format_spec.startswith('.getname>'):
            index = format_spec[9:]
            list = {}
            counter = 0
            for i in self._frames: 
                list[str(counter)] = i
                counter += 1
            try: return list[str(index)]
            except (KeyError) as e: 
                raise FrameComposeError(f'index<{index}>', 'GetItemError', f'Unknown key: {e}')
            except Exception as e: raise FrameComposeError(index, 'fStringError', e)
        elif format_spec.startswith('.safemode'):
            return str(self.__safemode)
        elif format_spec.startswith('.hash'):
            return str(self.__hash__())
        elif format_spec.startswith(('.sgc', '.superglobal', '.sgcname')): 
            return self.sgc._name
        elif format_spec.startswith(('.arch', '.a')): 
            return self._arch
        raise ValueError('Unknown format option.')
    def __hash__(self) -> int:
        arch = str_to_int(self._arch)
        frames = str_to_int(self._frames)
        safemode = str_to_int(self.__safemode)
        superglobal = str_to_int(self._superglobal_name)
        return arch+frames+safemode+superglobal
    def __int__(self):
        return self.__hash__()



if __name__ == '__main__':
    filename = 'fc'
    format = 'json'
    filepath = f'{filename}.{format}'
    with FramesComposer(safemode=False) as fc:
        fc['test1'] = Frame(safemode=False)
        fc['test2'] = Frame(safemode=False)
        @fc['test2'].register()
        def test():
            return 'compleate'
        with fc['test2'] as f:
            f.Var('x', 10)
            f.Var('y', 50)
            SystemOP.match('x > y', 'print("x bigger")', 'print("y bigger")')
            f.Var('test', Get('x') * Get('y')) 
            @f.register()
            def test(): 
                print('testing')
            @f.register()
            class Test():
                hello = 'World'
                pass
        @fc['test1'].register()
        def test():
            return 'compleate'
        mfc = MathPlugin(fc['test1']).include()
        mfc.discriminant(10, 20, 30)
        mfc.discriminant(20, 20, 80)
        fc.sync('test1', '$')
        fc.sync('test2', '$')
        fc.save(filepath, format)
    with FramesComposer.from_file(filepath, format) as fc:
        fc.test_exec()
        fc.deploy('test.py', 'fc.json', runing=True)

