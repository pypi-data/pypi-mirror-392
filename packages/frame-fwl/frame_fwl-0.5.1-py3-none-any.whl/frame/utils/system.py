import sys, ctypes, gc

def sizeof(OBJECT: object, *objects): 
    val = object.__sizeof__(OBJECT) if not objects else [
        object.__sizeof__(OBJECT), 
        *[
            object.__sizeof__(i) for i in objects
        ]
    ]
    return val

def malloc(size):
    return (ctypes.c_byte * size)()

def free(block):
    del block

def delete_trash():
    return gc.collect()