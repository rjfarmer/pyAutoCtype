import pyctype as pyc
import ctypes

x=pyc.cwrap('./tests/libtester.so')

x.list_structs()

z=x.test_struct
z.b=2
x.structFunc1(z)