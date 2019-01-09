#!/usr/bin/env python

import os
from setuptools import setup, find_packages

from distutils.core import setup, Extension

import os
import sysconfig

def get_version():
	with open("pyctype/version.py") as f:
		l=f.readlines()
	return l[0].split("=")[-1].strip().replace("'","")


setup(name='pyAutoCtype',
      version=get_version(),
      description='Auto generate ctype bindings',
      license="GPLv2+",
      author='Robert Farmer',
      author_email='r.j.farmer@uva.nl',
      url='https://github.com/rjfarmer/pyAutoCtype',
      keywords='python ctypes binding',
      packages=find_packages(),
      classifiers=[
			"Development Status :: 3 - Alpha",
			"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
		    'Topic :: Software Development :: Code Generators'
      ],
      test_suite = 'tests'
     )
