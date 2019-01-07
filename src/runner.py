import pyctype as pyc


x=pyc.cwrap('../test/libtester.so')

x.const_int.get()

x.const_int = 10

x.g_a_int.get()

x.g_a_int = 99

x.g_a_int.get()