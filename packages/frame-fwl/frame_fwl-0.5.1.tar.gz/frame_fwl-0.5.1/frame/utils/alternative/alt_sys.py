'''
# Alternative system methods.\n
Custom methods:
    __version__() 
        - get python version.
    __has_module__(module) 
        - check module instalation.
    __ch[mode](args)
        - cache function. Modes: get/set. In 'get' args is empty, 
          in 'set' args is [data] - data for cache.
    __bs 
        - class for __build_class__ change
Custom params:
    __has_cython__ - check for cython available.
Edited:
    sys.version - to custom version name.
'''


# imports and configs
import builtins, sys, abc

CYTHON_AVAILABLE = 1
try: import Cython
except ImportError: CYTHON_AVAILABLE = 0

builtins._cache_alternativemodule_env_ = 'NONE'
builtins.__bc = __build_class__




# build system
class BuildSystem(abc.ABC):
    def __init__(self):
        super().__init__()
        self.builds = []
    def _rebuild_(self, func, name: str, *args, metaclass = None):
        args = [func, name, *args, metaclass] if metaclass else [func, name, *args]
        self.builds.append(args)
        try: return builtins.__bc(*args)
        except TypeError: return BuildSystem()._rebuild_(*args)
    def __call__(self, *args, **kwds):
        return self.builds


# our methods
def get_ver():
    ver = sys.version.split('.')[:3]
    ver = ver[:2] + [ver[2].split(' ')[0]]
    return '.'.join(ver) + '.E#Pt' # Edited # (by) Pt

def ver(): return sys.version

def has_module(module_name: str): 
    try: __import__(module_name); return True
    except ImportError: return False

def set_cache(data):
    global builtins
    builtins._cache_alternativemodule_env_ = data

def get_cache(): return builtins._cache_alternativemodule_env_


# ===================================================================
# editing builtins to replace standart (to) and add ours functions
# while user use that module - our modules was imported like defaults
# ===================================================================

__version__ = ver
builtins.__version__ = __version__
sys.version = f'{get_ver()} - edited python by pt'
__has_cython__ = bool(CYTHON_AVAILABLE)
builtins.__has_cython__ = __has_cython__
__has_module__ = has_module
builtins.__has_module__ = __has_module__
__ch = {'get': get_cache, 'set': set_cache}
builtins.__ch = __ch
__bs = BuildSystem()
builtins.__bs = __bs