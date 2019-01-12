import ctypes
import numpy as np
from .parsedwarf import parseDwarf


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
        ('double',8): ctypes.c_double,
        
        ('_Bool',1): ctypes.c_bool,
        ('char',1): ctypes.c_char,
        }

_dictNpTypes = {
        ('int',1): np.dtype('i1'),
        ('int',2): np.dtype('i2'),
        ('int',4): np.dtype('i4'),
        ('int',8): np.dtype('i8'),

        ('unsigned int',1): np.dtype('u1'),
        ('unsigned int',2): np.dtype('u2'),
        ('unsigned int',4): np.dtype('u4'),
        ('unsigned int',8): np.dtype('u8'),

        ('float',4): np.dtype('f4'),
        
        ('float',8): np.dtype('f8'),
        ('double',8): np.dtype('f8'),
        
        ('_Bool',1): np.dtype('?'),
        }


class cwrap(object):
    def __init__(self, filename):
        self.filename = filename
        self._lib = ctypes.CDLL(filename)

        x = parseDwarf(filename)
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

    @property
    def value(self):
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


    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        return getattr(self.value, '__add__')(other)

    def __sub__(self, other):
        return getattr(self.value, '__sub__')(other)

    def __mul__(self, other):
        return getattr(self.value, '__mul__')(other)

    def __matmul__(self,other):
        return getattr(self.value, '__matmul__')(other)

    def __truediv__(self, other):
        return getattr(self.value, '__truediv__')(other)
        
    def __floordiv__(self,other):
        return getattr(self.value, '__floordiv__')(other)

    def __pow__(self, other, modulo=None):
        return getattr(self.value, '__pow__')(other,modulo)

    def __mod__(self,other):
        return getattr(self.value, '__mod__')(other)        
        
    def __lshift__(self,other):
        return getattr(self.value, '__lshift__')(other)        

    def __rshift__(self,other):
        return getattr(self.value, '__rshift__')(other)

    def __and__(self,other):
        return getattr(self.value, '__and__')(other)
        
    def __xor__(self,other):
        return getattr(self.value, '__xor__')(other)
        
    def __or__(self,other):
        return getattr(self.value, '__or__')(other)
        
    def __radd__(self, other):
        return getattr(self.value, '__radd__')(other)

    def __rsub__(self, other):
        return getattr(self.value, '__rsub__')(other)

    def __rmul__(self, other):
        return getattr(self.value, '__rmul__')(other)

    def __rmatmul__(self,other):
        return getattr(self.value, '__rmatmul__')(other)

    def __rtruediv__(self, other):
        return getattr(self.value, '__rtruediv__')(other)
        
    def __rfloordiv__(self,other):
        return getattr(self.value, '__rfloordiv__')(other)

    def __rpow__(self, other):
        return getattr(self.value, '__rpow__')(other)

    def __rmod__(self,other):
        return getattr(self.value, '__rmod__')(other)        
        
    def __rlshift__(self,other):
        return getattr(self.value, '__rlshift__')(other)        

    def __rrshift__(self,other):
        return getattr(self.value, '__rrshift__')(other)

    def __rand__(self,other):
        return getattr(self.value, '__rand__')(other)
        
    def __rxor__(self,other):
        return getattr(self.value, '__rxor__')(other)
        
    def __ror__(self,other):
        return getattr(self.value, '__ror__')(other)

    def __iadd__(self, other):
        self.set(self.value + other)
        return self.value

    def __isub__(self, other):
        self.set(self.value - other)
        return self.value

    def __imul__(self, other):
        self.set(self.value * other)
        return self.value

    def __itruediv__(self, other):
        self.set(self.value / other)
        return self.value

    def __ipow__(self, other, modulo=None):
        x = self.value**other
        if modulo:
            x = x % modulo
        self.set(x)
        return self.value

    def __eq__(self, other):
        return self.value == other

    def __neq__(self, other):
        return getattr(self.value, '__new__')(other)

    def __lt__(self, other):
        return getattr(self.value, '__lt__')(other)

    def __le__(self, other):
        return getattr(self.value, '__le__')(other)

    def __gt__(self, other):
        return getattr(self.value, '__gt__')(other)

    def __ge__(self, other):
        return getattr(self.value, '__ge__')(other)
        
    def __format__(self, other):
        return getattr(self.value, '__format__')(other)
  
    def __bytes__(self):
        return getattr(self.value, '__bytes__')()  
        
    def __bool__(self):
        return getattr(self.value, '__bool__')()
   
    def __len__(self):
        return getattr(self.value, '__len__')()

class cfunc(object):
    def __init__(self, lib, func, name):
        self.lib = lib
        self.name = name
        try:
            self.func = func['def']
        except KeyError:
            self.func = None
        self._args = func['args']

    def _init(self):
        if '_func' not in self.__dict__:
            self._func = getattr(self.lib, self.name)
            try:
                self._func.restype = makeCType(self.func) 
            except KeyError:
                self._func.restype = None

            # Set argtypes
            self._ctype_args = [makeCType(value['def']) for key, value in self._args.items()]
            self._func.argtypes = self._ctype_args


        return self._func

    def __call__(self,*args):
        if '_func' not in self.__dict__:
            self._init()

        return self._func(*args)



def makeCType(x,ptrs=True):
    try:
        res = _dictCTypes[(x['type'],x['size'])]
    except (KeyError, TypeError):
        return None

    if x['array']:
        dtype = _dictNpTypes[(x['type'],x['size'])]
        arr_len = len(x['array'])
        arr_shape = tuple([j-i+1 for i,j in x['array']])
        res = np.ctypeslib.ndpointer(dtype=dtype,
                ndim=arr_len,shape=arr_shape,flags='C')
        return res

    if ptrs:
        for i in range(x['ptrs']):
            res = ctypes.POINTER(res)

    return res