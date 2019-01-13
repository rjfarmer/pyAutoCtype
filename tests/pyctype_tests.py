import os, sys

os.environ["_PYAUTOCTYPE_TEST_FLAG"] = "1"

import numpy as np
import pyctype as pyc


import unittest
    
import subprocess
import numpy.testing as np_test

from contextlib import contextmanager
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO
    from io import BytesIO

os.chdir('tests')
subprocess.check_output(["make"])
x=pyc.cwrap('./libtester.so')


@contextmanager
def captured_output():
    """
    For use when we need to grab the stdout/stderr (but only in testing)
    Use as:
    with captured_output() as (out,err):
        func()
    output=out.getvalue().strip()
    error=err.getvalue().strip()
    """
    new_out, new_err = StringIO(),StringIO()
    old_out,old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class TestStringMethods(unittest.TestCase):
    def test_mising_var(self):	
        with self.assertRaises(KeyError) as cm:
            a=x.invalid_var.value

    def test_global_int(self):
        self.assertEqual(x.const_int,5)

    def test_global_const_int_set(self):
        with self.assertRaises(AttributeError) as cm:
            x.const_int = 5

    def test_global_int_set(self):
        x.g_a_int = 99
        self.assertEqual(x.g_a_int,99)   

    def test_call_void_func(self):
        x.setpPtr()

    def test_call_int_func(self):
        self.assertEqual(x.intFuncNoArgs(),42)

    def test_call_float_func(self):
        self.assertEqual(x.floatFuncNoArgs(),99.0)    

    def test_call_int_func1(self):
        self.assertEqual(x.intFunc1(5),10) 

    def test_call_int_func2(self):
        self.assertEqual(x.intFunc2(5,6),11)   

    def test_call_float_func1(self):
        self.assertEqual(x.floatFunc1(20.0),40.0)   

    def test_call_float_func2(self):
        y = x.floatFunc2(3.14,5.76)
        self.assertEqual(round(y,1),8.9)           

    def test_global_array_1d(self):
        y = x.int_arr

    def test_setStructS1(self):
        y = x.setStructS1()
        self.assertEqual(y,1)

        z = x.ts1_1
        self.assertTrue('a' in z)

        self.assertEqual(z['a'], 1)

        y = x.checkStructS1()
        self.assertEqual(y, 0)

        z['a'] = 3
        y = x.checkStructS1()
        self.assertEqual(y, 1)        



if __name__ == '__main__':
	unittest.main() 