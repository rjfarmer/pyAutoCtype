from __future__ import print_function

import struct
import copy

import parseElfHeader as elfH

            
elfstructs, elfdefines = elfH.processElfHeader()
            
class NotASharedObjectFile(Exception):
    pass

class NoDebugInfo(Exception):
    pass

class shared(object):
    _little = {'value':1,'order':'<'}
    _big =  {'value':2,'order':'>'}
    
    def __init__(self,filename):
        self.filename = filename
        self.bytesize = -1
        self.endianness = -1
        self.elfhead = []
        self.proghead = []
        self.sechead = []
        self.secnames = []
        self.data = None
        self.loadFile()
        self.unpack()
        
    def loadFile(self):
        with open(self.filename,'rb') as f:
            d = f.readlines()
        self.data = b"".join(d)
            
        self.checkFile()
        # Need to get bit size and endiness before full parsing 
        self.bytesize = self.getByteSize()
        self.endianness = self.getEndianness()
        
    def checkFile(self):
        if not self.data[:4]==b'\x7fELF':
            raise NotASharedObjectFile("Not a shared obejct file")
  
    def getByteSize(self):
        x = self.data[4]
        if x == 1:
            return elfstructs['x32']
        if x == 2:
            return elfstructs['x64']
        raise AttributeError("Bad byte size")
        
        
    def getEndianness(self):
        x = self.data[5]
        if x == 1:
            return self._little
        if x == 2:
            return self._big
        raise AttributeError("Bad endianness") 
        
    def unpackELFHeader(self):
        self.elfhead = self._getKeyValues(self.bytesize['Ehdr'], self.data)
  
    def _getKeyValues(self,struct,bytestr):
        struct.endianness(self.endianness)
        struct.unpack_from(bytestr)
        return copy.copy(struct)
        
    def unpackProgHead(self):
        start = self.elfhead['e_phoff']
        size = self.elfhead['e_phentsize']
        for i in range(self.elfhead['e_phnum']):
            x = self._getKeyValues(self.bytesize['Phdr'], self.data[start:start+size])
            self.proghead.append(x)
            start = start + size
        
    def unpackSecHead(self):
        start = self.elfhead['e_shoff']
        size = self.elfhead['e_shentsize']
        for i in range(self.elfhead['e_shnum']):
            x = self._getKeyValues(self.bytesize['Shdr'], self.data[start:start+size])
            self.sechead.append(x) 
            start = start + size
        self._setSecNames()
            
    def _getSecNames(self):
        offset = self.elfhead['e_shstrndx']
        sechead = self.sechead[offset]
        num_secs = self.elfhead['e_shnum']
        start = sechead['sh_offset']
        size = sechead['sh_size']
        self.secnames = self.data[start:start+size]
        
    def _setSecNames(self):
        self._getSecNames()
        for i in self.sechead:
            offset = i['sh_name']
            n = []
            while True:
                if self.secnames[offset] == 0:
                    break
                else:
                    n.append(self.secnames[offset:offset+1])
                    offset = offset +1
            n = b''.join(n).decode()
            i['sh_name'] = n
            
    def unpack(self):
        self.unpackELFHeader()
        self.unpackProgHead()
        self.unpackSecHead()
        
    def getDebugSecs(self):
        res = {}
        for i in self.sechead:
            if '.debug_' in i['sh_name']:
                res[i['sh_name']] = self.data[i['sh_offset']:i['sh_offset']+i['sh_size']]
            if '.dwo' in i['sh_name']:
                raise NoDebugInfo("Split debug info not supported")
        
        if len(res) == 0:
            raise NoDebugInfo("No debug symbols present, recompile with -g")
            
        if '.stab' in res:
            raise NoDebugInfo("Only works with dwarf debug symbols")
                
        return res
