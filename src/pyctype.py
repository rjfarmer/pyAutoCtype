import ctypes
import numpy as np
import parsedwarf as pd


_dictCTypes = {
        ('int',1): ctypes.c_int8,
        ('int',2): ctypes.c_int16,
        ('int',4): ctypes.c_int32,
        ('int',8): ctypes.c_int64,

        ('unsigned int',1): ctypes.c_uint8,
        ('unsigned int',2): ctypes.c_uint16,
        ('unsigned int',4): ctypes.c_uint32,
        ('unsigned int',8): ctypes.c_uint64,

        ('float',4): ctypes.c_float,
        
        ('float',8): ctypes.c_double,
        ('double',4): ctypes.c_double,
        
        ('_Bool',1): ctypes.c_bool,
        ('char',1): ctypes.c_char
        }


class cwrap(object):
    def __init__(self, filename):
        self.filename = filename
        self._lib = ctypes.CDLL(filename)

        x = pd.parseDwarf('../test/libtester.so')
        self._funcs = x['funcs']
        self._var = x['var']
        self._structs = x['structs']


    def __dir__(self):
        return list(self._var.keys()) + list(self._funcs.keys())

    def _init_var(self, name):
        if hasattr(self._var[name],'_init'):
            return
        
        self._var[name] = cvar(self._lib, self._var[name], name)


    def _init_func(self, name):
        if hasattr(self._funcs[name],'_init'):
            return

        self._funcs[name] = cfunc(self._lib, self._funcs[name], name)


    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            if '_var'  in self.__dict__ and name in self._var:
                self._init_var(name)
                return self._var[name]
            elif '_funcs'  in self.__dict__ and name in self._funcs:
                self._init_func(name)
                return self._funcs[name]
        
        return self.__dict__[name]

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
            return
        else:
            if '_var'  in self.__dict__ and name in self._var:
                self._init_var(name)
                self._var[name].set(value)
                return
        
        self.__dict__[name] = value


class cvar(object):
    def __init__(self, lib, var, name):
        self.lib = lib
        self.name = name
        self.var = var['def']
        self._init = True
        self._ctype = makeCType(self.var)

    def get(self):
        x = self._ctype.in_dll(self.lib, self.name)
        if x is None:
            return None

        if hasattr(x,'value'):
            return self._ctype.in_dll(self.lib, self.name).value
        else:
            while True:
                try:
                    x = x.contents
                except AttributeError:
                    break
            return x.value

    def set(self, value):
        if self.var['const']:
            raise AttributeError('Cant set const variable')
        else:
            if hasattr(self._ctype,'contents'):
                t = makeCType(self.var,False)
                print(t,t(value))
                self._ctype(t(value))
            else:
                self._ctype.in_dll(self.lib, self.name).value = value

class cfunc(object):
    def __init__(self, lib, func, name):
        self.lib = lib
        self.name = name
        self.func = func['def']
        self._init = True

    def get(self):
        return getattr(self.lib, self.name)


def makeCType(x,ptrs=True):
    try:
        res = _dictCTypes[(x['type'],x['size'])]
    except KeyError:
        res = None

    if ptrs:
        for i in range(x['ptrs']):
            res = ctypes.POINTER(res)

    return res