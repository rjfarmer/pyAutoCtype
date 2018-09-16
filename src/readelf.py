#!/usr/bin/env python
#-------------------------------------------------------------------------------
# scripts/readelf.py
#
# A clone of 'readelf' in Python, based on the pyelftools library
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os, sys
from optparse import OptionParser
import string
import io


from elftools import __version__
from elftools.common.exceptions import ELFError
from elftools.common.py3compat import (
        ifilter, byte2int, bytes2str, itervalues, str2bytes)
from elftools.elf.elffile import ELFFile
from elftools.elf.dynamic import DynamicSection, DynamicSegment
from elftools.elf.enums import ENUM_D_TAG
from elftools.elf.segments import InterpSegment, NoteSegment
from elftools.elf.sections import SymbolTableSection
from elftools.elf.gnuversions import (
    GNUVerSymSection, GNUVerDefSection,
    GNUVerNeedSection,
    )
from elftools.elf.relocation import RelocationSection
from elftools.elf.descriptions import (
    describe_ei_class, describe_ei_data, describe_ei_version,
    describe_ei_osabi, describe_e_type, describe_e_machine,
    describe_e_version_numeric, describe_p_type, describe_p_flags,
    describe_sh_type, describe_sh_flags,
    describe_symbol_type, describe_symbol_bind, describe_symbol_visibility,
    describe_symbol_shndx, describe_reloc_type, describe_dyn_tag,
    describe_ver_flags, describe_note
    )
from elftools.elf.constants import E_FLAGS
from elftools.dwarf.dwarfinfo import DWARFInfo
from elftools.dwarf.descriptions import (
    describe_reg_name, describe_attr_value, set_global_machine_arch,
    describe_CFI_instructions, describe_CFI_register_rule,
    describe_CFI_CFA_rule,
    )
from elftools.dwarf.constants import (
    DW_LNS_copy, DW_LNS_set_file, DW_LNE_define_file)
from elftools.dwarf.callframe import CIE, FDE


class ReadElf(object):
    """ display_* methods are used to emit output into the output stream
    """
    def __init__(self, filename):
        """ file:
                filename to read

            output:
                output stream to write to
        """
        with open(filename,'rb') as f:
            data = f.read()
        
        self.elffile = ELFFile(io.BytesIO(data))
        self.output = sys.stdout

        # Lazily initialized if a debug dump is requested
        self._dwarfinfo = None
        self._init_dwarfinfo()

        self._versioninfo = None
        self._init_versioninfo()

    def display_symbol_tables2(self):
        """ Display the symbol tables contained in the file
        """
        self._init_versioninfo()
        result = {}
        for section in self.elffile.iter_sections():
            if not isinstance(section, SymbolTableSection):
                continue

            if section['sh_entsize'] == 0:
                continue

            for nsym, symbol in enumerate(section.iter_symbols()):

                version_info = ''
                # readelf doesn't display version info for Solaris versioning
                if (section['sh_type'] == 'SHT_DYNSYM' and
                        self._versioninfo['type'] == 'GNU'):
                    version = self._symbol_version(nsym)
                    if (version['name'] != symbol.name and
                        version['index'] not in ('VER_NDX_LOCAL',
                                                 'VER_NDX_GLOBAL')):
                        if version['filename']:
                            # external symbol
                            version_info = '@%(name)s (%(index)i)' % version
                        else:
                            # internal symbol
                            if version['hidden']:
                                version_info = '@%(name)s' % version
                            else:
                                version_info = '@@%(name)s' % version

                if symbol['st_info']['bind'] == 'STB_GLOBAL' and symbol['st_info']['type'] != 'STT_NOTYPE':
                    result[symbol.name] = {'type':symbol['st_info']['type']}
        return result
                
    def _init_versioninfo(self):
        """ Search and initialize informations about version related sections
            and the kind of versioning used (GNU or Solaris).
        """
        if self._versioninfo is not None:
            return

        self._versioninfo = {'versym': None, 'verdef': None,
                             'verneed': None, 'type': None}

        for section in self.elffile.iter_sections():
            if isinstance(section, GNUVerSymSection):
                self._versioninfo['versym'] = section
            elif isinstance(section, GNUVerDefSection):
                self._versioninfo['verdef'] = section
            elif isinstance(section, GNUVerNeedSection):
                self._versioninfo['verneed'] = section
            elif isinstance(section, DynamicSection):
                for tag in section.iter_tags():
                    if tag['d_tag'] == 'DT_VERSYM':
                        self._versioninfo['type'] = 'GNU'
                        break

        if not self._versioninfo['type'] and (
                self._versioninfo['verneed'] or self._versioninfo['verdef']):
            self._versioninfo['type'] = 'Solaris'

    def _symbol_version(self, nsym):
        """ Return a dict containing information on the
                   or None if no version information is available
        """

        symbol_version = dict.fromkeys(('index', 'name', 'filename', 'hidden'))

        if (not self._versioninfo['versym'] or
                nsym >= self._versioninfo['versym'].num_symbols()):
            return None

        symbol = self._versioninfo['versym'].get_symbol(nsym)
        index = symbol.entry['ndx']
        if not index in ('VER_NDX_LOCAL', 'VER_NDX_GLOBAL'):
            index = int(index)

            if self._versioninfo['type'] == 'GNU':
                # In GNU versioning mode, the highest bit is used to
                # store wether the symbol is hidden or not
                if index & 0x8000:
                    index &= ~0x8000
                    symbol_version['hidden'] = True

            if (self._versioninfo['verdef'] and
                    index <= self._versioninfo['verdef'].num_versions()):
                _, verdaux_iter = \
                        self._versioninfo['verdef'].get_version(index)
                symbol_version['name'] = next(verdaux_iter).name
            else:
                verneed, vernaux = \
                        self._versioninfo['verneed'].get_version(index)
                symbol_version['name'] = vernaux.name
                symbol_version['filename'] = verneed.name

        symbol_version['index'] = index
        return symbol_version

    def _init_dwarfinfo(self):
        """ Initialize the DWARF info contained in the file and assign it to
            self._dwarfinfo.
            Leave self._dwarfinfo at None if no DWARF info was found in the file
        """
        if self._dwarfinfo is not None:
            return

        if self.elffile.has_dwarf_info():
            self._dwarfinfo = self.elffile.get_dwarf_info()
        else:
            self._dwarfinfo = None
            
            
    def getDebugInfo(self):
        z = self._getDebugInfo()
        z = self._cleanDebugInfo(z)
        z = self._processDebugInfo(z)
        
        return z

    def _getDebugInfo(self):
        """ Dump the debugging info section.
        """
        set_global_machine_arch(self.elffile.get_machine_arch())
        _ = self._dwarfinfo.debug_info_sec.name
        # Offset of the .debug_info section in the stream
        section_offset = self._dwarfinfo.debug_info_sec.global_offset

        for cu in self._dwarfinfo.iter_CUs():
            # The nesting depth of each DIE within the tree of DIEs must be
            # displayed. To implement this, a counter is incremented each time
            # the current DIE has children, and decremented when a null die is
            # encountered. Due to the way the DIE tree is serialized, this will
            # correctly reflect the nesting depth
            #
            die_depth = 0
            r = []
            for die in cu.iter_DIEs():
                r.append({})
                r[-1]['depth'] = die_depth
                r[-1]['offset'] = die.offset
                r[-1]['abbrev'] = die.abbrev_code
                r[-1]['tag'] = die.tag
                if die.is_null():
                    die_depth -= 1
                    continue

                r[-1]['attr'] = {}
                for attr in itervalues(die.attributes):
                    name = attr.name
                    r[-1]['attr'][name] = describe_attr_value(
                            attr, die, section_offset).replace('\t','')
                if die.has_children:
                    die_depth += 1
        return r
        
    def _cleanDebugInfo(self, debug):
        ''' Matches children to parents and removes them from the top level of the dict '''
        parent = debug[0]
        remove = []
        parent['child'] = []
        for idx,i in enumerate(debug):
            if i['depth'] == 1:
                parent = i
                parent['child'] = []
            if i['depth'] == 2:
                parent['child'].append(i)
                remove.append(idx)
        for i in reversed(remove):
            del debug[i]

        return debug
        
    def _processDebugInfo(self, debug):
        r = {}
        for i in debug:
            if 'attr' in i and 'DW_AT_decl_file' in i['attr']:
                if i['attr']['DW_AT_decl_file'] == '1':
                    # Things we care about
                    if 'DW_AT_name' in i['attr']:
                        n = i['attr']['DW_AT_name'].split(':')[-1].strip()
                    else:
                        # make temp name
                        n = i['offset']
                    r[n] = i
                    r[n]['args'] = {}
                    for j in i['child']:
                        if 'attr' in j:
                            [j.pop(k,None) for k in ['depth','DW_AT_name','DW_AT_low_pc','DW_AT_high_pc','DW_AT_frame_base','DW_AT_location']]
                            r[n]['args'][j['attr']['DW_AT_name']] = j
                    [r[n].pop(k,None) for k in ['depth','child','DW_AT_name','DW_AT_low_pc','DW_AT_high_pc','DW_AT_frame_base','DW_AT_location']]
        return r
