
PHONY: all

FC = gfortran

ifdef TRAVIS
	FC = $(TRAVIS_GFORTRAN)
endif

OPTIONS = -ggdb3 -fPIC -shared


all:
	gfortran  $(OPTIONS) -c test2.f90
	gfortran $(OPTIONS) -o tester.so test_mod.f90 test2.f90
	gcc -ggdb3 -fPIC -shared -o libtester.so test.c

# Macros added at -ggdb3 level

