import pyctype as pyc
import ctypes

x=pyc.cwrap('./tests/libtester.so')
y = x.test_struct
