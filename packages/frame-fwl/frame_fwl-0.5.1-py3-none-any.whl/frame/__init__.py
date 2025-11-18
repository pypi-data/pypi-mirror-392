'''
# FRAME
Multi-functional framework combining many functions and the collection of several libraries. 

## Basic concepts -
    #### Frames
    The concept allows creating isolated contexts with its own variables, deferred execution of code and possibility to save a frame in a file.
    Main terms - 
        - Frame - An isolated execution space with its own variables and code. Can interact with other contexts.
        - Framing - creating a local environment with superglobal variables.
        - Superglobal is the state of an object when it does not depend on the context. Roughly speaking, a global frame.
        - Framefile is a binary frame image that can be saved and loaded.

    #### Nets
    Library concept with functions for white/grey hacking, testing and education.
'''


from .frame_core import (
    FramesComposer, 
    Frame, 
    Framer, 
    FastGet, 
    fOp, 
    fGet, 
    fCode, 
    fExec, 
    fReturn, 
    fSys, 
    fVar, 
    exec_and_return, 
    exec_and_return_safe,
    save_code_to_bin, 
    open_and_run,
    str_to_int,
    framing_result,
    framing,
    FrameApiError, 
    FrameExecutionError, 
    FramerError, 
    FramingError, 
    PluginError, 
    PluginIsNotWorkingError,
    PluginBase, 
    PluginRegistry, 
    MathPlugin, 
    register_plugin
)
from .nets_core import (
    HackModuleApi,
    HashCryptoApi,
    RandCryptoApi,
    DatsSecureApi,
    GrayHackApi,
    WhiteHackApi
)
from .nets_plugin import (
    NetsPlugin
)