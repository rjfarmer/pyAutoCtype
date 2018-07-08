from __future__ import print_function
import ctypes
import collections
from elftools.elf.elffile import ELFFile


import utils


filename = '../test/libtester.so'

def loadFile(filename):
    f=open(filename,'rb')
    elffile = ELFFile(f)
    
    if not elffile.has_dwarf_info():
        f.close()
        raise ValueError("No debug symbols found")
    
    return elffile.get_dwarf_info()
    
def get_name_val(element):
	try:
		x = {
			'type':element.attributes['DW_AT_type'].value,
			'form':element.attributes['DW_AT_type'].form #bytesize?
			}
	except KeyError:
		x = None
	
	return element.attributes['DW_AT_name'].value.decode(),x

x=loadFile(filename)
#def get_meta(dwarf):

dwarf=x
res={}
for CU in dwarf.iter_CUs():
	top = CU.get_top_DIE() 
	fname = top.attributes['DW_AT_name'].value.decode()
	folder = top.attributes['DW_AT_comp_dir'].value.decode()
	language = int(top.attributes['DW_AT_language'].value)
	res[fname] = {'folder':folder,'laguage':utils.get_language(language)} 
	
	if top.has_children:
		res[fname]['comp'] = collections.OrderedDict()
		for i in top.iter_children():
			name, val = get_name_val(i)
			res[fname]['comp'][name]=val
