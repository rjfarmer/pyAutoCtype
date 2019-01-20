import ctypes
import numpy as np
import struct

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

_dictStTypes = {
        ('int',1): 'b',
        ('int',2): 'h',
        ('int',4): 'i',
        ('int',8): 'q',
        
        ('unsigned int',1): 'B',
        ('unsigned int',2): 'H',
        ('unsigned int',4): 'I',
        ('unsigned int',8): 'Q',

        ('float',4): 'f',
        
        ('float',8): 'd',
        ('double',8): 'd',
        
        ('_Bool',1): '?',
        ('char',1): 'c',
        }

_allStructsBase = {}

class cwrap(object):
    def __init__(self, filename):
        global _allStructsBase
        self.filename = filename
        self._lib = ctypes.CDLL(filename)

        x = parseDwarf(filename)
        self._funcs = x['funcs']
        self._var = x['var']
        self._structs = x['structs']
        _allStructsBase = x['structs']

    def __dir__(self):
        return list(self._var.keys()) + list(self._funcs.keys()) + list(self._structs.keys()) 

    def _init_var(self, name):
        if hasattr(self._var[name],'_init'):
            return
        
        self._var[name] = cvar(self._lib, self._var[name], name)


    def _init_func(self, name):
        if hasattr(self._funcs[name],'_init'):
            return

        self._funcs[name] = cfunc(self._lib, self._funcs[name], name)

    def _init_struct(self, name):
        if name in self._var:
            return

        # Insert struct into variable defintions so we unify
        # access through cvar
        self._var[name] = cvar(self._lib, self._structs[name], name)


    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            if '_var' in self.__dict__ and name in self._var:
                self._init_var(name)
                return self._var[name]

            elif '_funcs' in self.__dict__ and name in self._funcs:
                self._init_func(name)
                return self._funcs[name]

            elif '_structs' in self.__dict__ and name in self._structs:
                self._init_struct(name)
                return self._var[name]       
        
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
    def __init__(self, lib, var , name = None):
        self.lib = lib
        self.var = var['def']
        self._ctype = makeCType(self.var)
        self.name = name
        self._init = True

        if self.name is not None:
            self.in_dll()

    def from_param(self,obj):
        return self._ctype.from_param(obj)

    def from_address(self, address):
        return self._ctype.from_address(address)

    def from_buffer(self, source, offset=0):
        return self._ctype.from_buffer(source, offset)

    def from_buffer_copy(self, source, offset=0):
        return self._ctype.from_buffer_copy(source, offset)

    def in_dll(self):
        return self._ctype.in_dll(self.lib, self.name)

    @property
    def value(self):
        x = self._ctype.in_dll(self.lib, self.name)
        if x is None:
            return None

        if hasattr(x,'value'):
            return x.value
        else:
            while True:
                try:
                    x = x.contents
                except AttributeError:
                    break
            if hasattr(x,'value'):
                return x.value
            else:
                return x


    def set(self, value):
        if self.var['const']:
            raise AttributeError('Can not set const variable')
        else:
            if hasattr(self._ctype,'contents'):
                self._ctype(value)
            else:
                self.in_dll().value = value

    @property
    def _as_parameter_(self):
        return self._ctype._as_parameter_


    def __getitem__(self, key):
        if self.var['struct']:
            return self._ctype[key]
        else:
            raise TypeError('Not subscriptable')

    def __setitem__(self, key, value):
        if self.var['struct']:
            self._ctype[key] = value
        else:
            raise TypeError('Not subscriptable')

    def __contains__(self, key):
        if self.var['struct']:
            return key in self._ctype
        else:
            raise TypeError('Not subscriptable')

    def __dir__(self):
        if self.var['struct']:
            return self._ctype.keys()

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
        return self.value != other

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

        a = []
        for ain,atype in zip(args,self._args.values()):
            if atype['def']['ptrs']:
                a.append(make_pointer_argsvalues(ain, atype['def']))
            else:
                a.append(ain)

        return self._func(*a)


def makeCType(x,ptrs=True):
    res = None
    try:
        res = _dictCTypes[(x['type'],x['size'])]
    except TypeError:
        return None
    except KeyError:
        pass

    if x['struct']:
        res = cstruct(_allStructsBase[x['type']])

    if ptrs and x['ptrs']>0:
        res = make_pointer_argtypes(res, x)

    return res


def make_pointer_argtypes(value, cctype):
    if cctype['ptrs']>0:
        if cctype['struct']:
            res = ctypes.POINTER(value._bufferType)
            nptrs = cctype['ptrs'] - 1
        else:
            nptrs = cctype['ptrs']
            res = value
        
        if nptrs > 0:
            for i in range(nptrs):
                res = ctypes.POINTER(res)  

    return res

def make_pointer_argsvalues(value, cctype):
    if cctype['ptrs']>0:
        if cctype['struct']:
            res = ctypes.pointer(value._ctype._buffer)
            nptrs = cctype['ptrs'] - 1
        else:
            nptrs = cctype['ptrs']
            res = value
        
        if nptrs > 0:
            for i in range(nptrs):
                res = ctypes.pointer(res)  

    return res


class cstruct(ctypes.Structure):
    def __init__(self, structType):
        self._structType = structType
        self._args = self._structType['args']

        self._bufferType = ctypes.c_char * structType['def']['size']
        self._buffer = self._bufferType()
        self._init = True

    def __getitem__(self, key):
        if not key in self.keys():
            raise KeyError("No key "+str(key))

        return self._unpack(key)
        

    def __setitem__(self, key, value):
        if not key in self.keys():
            raise KeyError("No key "+str(key))

        self._pack(key, value)

    def _parseArg(self, key):
        arg = self._args[key]
        abytes = b''

        start = arg['loc'] 
        adef =  arg['def']
        end = start + adef['size']

        if adef['struct'] or adef['union']:
            pass
        
        if adef['array']:
            pass
        
        if adef['ptrs'] > 0:
            pass

        typeTuple = (adef['type'],adef['size'])
        sc = ''
        if typeTuple in _dictStTypes:
            sc = '@'+_dictStTypes[typeTuple]

        return start, end, sc

    def _unpack(self, key):
        start, end, sc = self._parseArg(key)
        return struct.unpack(sc, self._buffer[start:end])[0]

    def _pack(self, key, value):
        start, end, sc = self._parseArg(key)
        struct.pack_into(sc, self._buffer, start, value)

    def keys(self):
        return self._args.keys()

    def __contains__(self,key):
        return key in self.keys()

    def __dir__(self):
        return self.keys()


    def from_param(self, obj):
        return self._buffer

    def in_dll(self, lib, name):
        try:
            self._buffer = self._bufferType.in_dll(lib,name)
        except ValueError:
            pass
        return self._buffer

    @property
    def _as_parameter_(self):
        return self._buffer