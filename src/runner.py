import pyctype as pyc


x=pyc.cwrap('../test/libtester.so')

x.p_b_float = 1.0

x.p_b_float
