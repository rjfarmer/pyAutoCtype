import pyctype as pyc
import ctypes

x=pyc.cwrap('./tests/libtester.so')
x.setStructS1()

class ss(ctypes.Structure):
    _fields_ = [('a',ctypes.c_int32),
                ('b',ctypes.c_float)
    ]

a=ctypes.ss.in_dll(x._lib,'ts1_1')



ctypes.c_int32.from_address(a.value)

