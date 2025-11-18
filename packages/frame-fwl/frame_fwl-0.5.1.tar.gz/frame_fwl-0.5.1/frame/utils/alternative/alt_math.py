'''
# Alternative math. 

'''



# imports
import ctypes, sys, builtins, abc
from decimal import Decimal, getcontext


# our methods
def superlarge(x):
    '''creating large integrer from [x]'''
    res = x
    for i in range(x): 
        k = (i if i != 0 else 1)
        res **= k if x <= 9**99 else k / 3
    return res

def supersmall(x):
    '''creating small float from [x]'''
    res = x
    for i in range(x+x): res *= eval(f'0.{i}' if i != 0 else '1')
    return res

def re_pow(x):
    '''creating alternative 'power' operations to create float from [x]. like 'normalization'.'''
    res = x
    for i in range(x+x): 
        evaled = eval(f'0.{i}' if i != 0 else '0')
        res -= evaled if res - evaled >= 0 else -evaled
    return res

def setmax(number: int):
    'set max digits in int'
    getcontext().prec = number
    sys.set_int_max_str_digits(number)




# ===================================================================
# editing builtins to replace standart (to) and add ours functions
# while user use that module - our modules was imported like defaults
# ===================================================================

FLOAT = float

class nw_float(Decimal): # new float
    @classmethod
    def fromhex(cls, string: str) -> Decimal: 
        float_num = FLOAT.fromhex(string)
        return cls(float_num)
    @classmethod
    def hex(cls, float: FLOAT) -> str:
        return FLOAT.hex(FLOAT(float))
    @classmethod
    def is_integer(cls, number) -> bool:
        return FLOAT.is_integer(FLOAT(number))
        
builtins.float = nw_float

class cl_float(float):... # classic float
builtins.cl_float = cl_float

dFLOAT = float

def set_default_float(): 
    global builtins
    builtins.float = FLOAT

def set_decimal_float(): 
    global builtins
    builtins.float = dFLOAT

def set_alt_funcs():
    global builtins
    builtins.superlarge = superlarge
    builtins.supersmall = supersmall
    builtins.repow = re_pow

    builtins._dfl_float = set_default_float
    builtins._new_float = set_default_float

def replace_alt_funcs():
    import builtins as nbins
    global builtins
    builtins = bin

class alt_math:
    def __init__(self, max: int = 4300):
        self.max = max
    def enable(self):
        set_decimal_float()
        set_alt_funcs()
        setmax(self.max)
    def disable(self):
        set_default_float()
        replace_alt_funcs()
        setmax(4300)
    def __enter__(self, *args):
        self.enable(); return self
    def __exit__(self, *args):
        self.disable()

builtins.__setmax__ = setmax
builtins.__altmath__ = alt_math
