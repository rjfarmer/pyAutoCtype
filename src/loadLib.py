from __future__ import print_function
import ctypes
from elftools.elf.elffile import ELFFile


filename = 'test/libtester.so'

def loadFile(filename):
    f=open(filename,'rb')
    elffile = ELFFile(f)
    
    if not elffile.has_dwarf_info():
        f.close()
        raise ValueError("No debug symbols found")
    
    return elffile.get_dwarf_info()


def get_meta(dwarf):
    res={}
    for CU in dwarf.iter_CUs():
        top = CU.get_top_DIE() 
        name = top['']



x=loadFile(filename)
get_meta(x)

        


