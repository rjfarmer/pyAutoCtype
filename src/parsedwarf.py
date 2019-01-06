from __future__ import print_function

import sys

from collections import OrderedDict
import itertools

from elftools.common.py3compat import itervalues
from elftools.elf.elffile import ELFFile
from elftools.dwarf.descriptions import (
    describe_DWARF_expr, set_global_machine_arch)
from elftools.dwarf.locationlists import LocationEntry


def listDIES(DIE):
    for k,v in DIE.items():
        try:
            print(k,v.tag,v.attributes['DW_AT_name'].value)
        except KeyError:
            pass

def listDIES2(DIE):
    for k,v in DIE.items():
        try:
            print(k,v.tag)
        except KeyError:
            pass


def process_file(filename):
    print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)
        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return
        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        dwarfinfo = elffile.get_dwarf_info()
        # This is required for the descriptions module to correctly decode
        # register names contained in DWARF expressions.
        set_global_machine_arch(elffile.get_machine_arch())
        alldies=OrderedDict()
        for CU in dwarfinfo.iter_CUs():
            # A CU provides a simple API to iterate over all the DIEs in it.
            for DIE in CU.iter_DIEs():
                alldies[DIE.offset] = DIE
    return alldies
    
DIE =  process_file('../test/libtester.so')
    
def getAttr(DIE):
    res = OrderedDict()
    res['offset'] = DIE.offset
    for attr in itervalues(DIE.attributes):
        if attr.name == 'DW_AT_name':
            res['name']=attr.value.decode()
        if attr.name == 'DW_AT_type':
            res['type_num']=attr.value
        # if attr.name == 'DW_AT_decl_file':
        #     res['file']=attr.value
        # if attr.name == 'DW_AT_decl_line':
        #     res['line']=attr.value
        if attr.name == 'DW_AT_data_member_location':
            res['loc'] = attr.value
        if attr.name == 'DW_AT_byte_size':
            res['bytes'] = attr.value
        if attr.name == 'DW_TAG_array_type':
            res['array'] = attr.value
        if attr.name == 'DIE DW_TAG_pointer_type':
            res['ptr'] = True
            
    return res



def parseBT(base_type, x):
    for k in x:
        if 'type_num' in x[k]:
            if x[k]['type_num'] in base_type:
                bt = base_type[x[k]['type_num']]
                if 'def' in bt:
                    x[k]['def'] = bt['def']
        if 'args' in x[k]:
            x[k].args = parseBT(base_type, x[k]['args'])
    return x

def parseType(DIE, child):
    name = ''
    size = -1
    struct=False
    array=False
    const=False
    union=False
    num_ptrs = 0

    while True:
        try:
            name = child.attributes['DW_AT_name'].value.decode()
        except KeyError:
            pass

        try:
            size = child.attributes['DW_AT_byte_size'].value
        except KeyError:
            pass

        if child.tag == 'DW_TAG_typedef':
            size = -1
            struct = True

        if child.tag == 'DW_TAG_array_type':
            array = True

        if child.tag == 'DW_TAG_const_type':
            const = True
        
        if child.tag == 'DW_TAG_pointer_type':
            num_ptrs = num_ptrs + 1      

        if child.tag == 'DW_TAG_union_type':
            union = True

        try:
            if child.attributes['DW_AT_type'].value in DIE:
                child = DIE[child.attributes['DW_AT_type'].value]
        except KeyError:
            break


    output = {'name':name,
            'ptrs':num_ptrs,
            'size':size,
            'struct':struct,
            'array':array,
            'const':const,
            'union':union}

    return output


def parseDIE(DIEs):
    funcs = OrderedDict()
    var = OrderedDict()
    base_type = OrderedDict()
    structs = OrderedDict()

    bt = set(['DW_TAG_base_type', 'DW_TAG_member', 
                'DW_TAG_pointer_type','DW_TAG_array_type',
                'DW_TAG_const_type'])

    bt2 = set(['DW_TAG_typedef', 'DW_TAG_union_type'])

    for key,value in DIEs.items():
        if value.tag == "DW_TAG_subprogram":
            x = getAttr(value) 
            n = x['name']
            funcs[n] = x 
            funcs[n]['args'] = OrderedDict()
            for j in value.iter_children():
                x2 = getAttr(j)
                funcs[n]['args'][x2['name']] = x2
        if value.tag == "DW_TAG_variable":
            x = getAttr(value)
            n = x['name']
            var[n] = x
        if value.tag in bt:
            x = getAttr(value)
            base_type[x['offset']] = x
            base_type[x['offset']]['def'] = parseType(DIE, value)
        if value.tag in bt2:
            x = getAttr(value)
            n = x['name']
            structs[n] = x   
            structs[n]['args'] = OrderedDict()    
            base_type[x['offset']] = x
            base_type[x['offset']]['def'] = parseType(DIE, value)
            # Get the definition:
            try:
                st = DIEs[value.attributes['DW_AT_type'].value]
            except KeyError:
                continue
            # Get elements of struct:
            for j in st.iter_children():
                x2 = getAttr(j)
                structs[n]['args'][x2['name']] = x2            

    var = parseBT(base_type,var)
    funcs = parseBT(base_type, funcs)
    structs = parseBT(base_type,structs)
                
    return funcs, var, base_type, structs


funcs, var, base_type, structs = parseDIE(DIE)




