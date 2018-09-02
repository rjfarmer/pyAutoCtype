import struct

class elfstruct(object):
    def __init__(self,struct):
        self._s = struct
        self._bytes = self._s
        self._endianness = None
        
    def endianness(self, e):
        self._endianness = e
        self.set_struct()
        
    def format(self):
        return self._endianness['order'] + ''.join(self._s.values())
        
    def set_struct(self):
        self.struct = struct.Struct(self.format())
    
    def unpack_from(self, bytestr):
        self._bytes = {}
        b = self.struct.unpack_from(bytestr)
        ind = 0
        f = self.format()
        for key, value in self._s.items():
            x = b[ind:ind+len(value)]
            x = b[ind:ind+len(value)]
            if len(x) == 1:
                x=x[0]
            self._bytes[key] = x
            ind = ind + len(value)
    
    def size(self):
        return self.struct.size
    
    def keys(self):
        return self._s.keys()
        
    def items(self):
        return self._bytes.items()

    def values(self):
        return self._bytes.values()
        
    def __getitem__(self, key):
        return self._bytes[key]
        
    def __setitem__(self, key, value):
        self._bytes[key] = value
        
    def __repr__(self):
        return self._bytes.__repr__()

    def __str__(self):
        return self._bytes.__str__()

    def __len__(self):
        return self._bytes.__len__()
        
    def __dir__(self):
        return self._bytes.__dir__()
        
    def __contains__(self, key):
        return self._bytes.__contains__(key)

    def __copy__(self):
        new_obj = type(self)(self._s)
        new_obj.__dict__.update(self.__dict__)
        return new_obj

class elfdefines(object):
    def __init__(self,d):
        self._d = d

    def find_key(self,keyroot,value):
        
        d = self._find(keyroot)
        if isinstance(d,dict):
            for k,v in d.items():
                if v == value:
                    return keyroot + '_' + k
        elif d == value:
            return keyroot
        else:
            raise KeyError("Cant find " + str(keyroot))
        
    def find_value(self,keyroot):
        
        d = self._find(keyroot)
        if isinstance(d,dict):
            raise KeyError("keyroot is not unique" + str(keyroot))
        else:
            return d
        
    def _find(self,keyroot):
        k = keyroot.split('_')
        d = self._d
        for idx,i in enumerate(k):
            if isinstance(d,dict):
                try:
                    d = d[i]
                except KeyError:
                    raise KeyError("Cant find "+'_'.join(k[:idx+1]))
        
        return d
        


def processElfHeader(filename='/usr/include/elf.h'):
    with open(filename,'r') as f:
        lines=f.readlines()
        
    def remove_index(lines,indexes):
        for i in indexes[::-1]:
            lines.pop(i)
        return lines
    
    remove=[]
    for idx,i in enumerate(lines):
        i = i.strip()
        if len(i) == 0:
            remove.append(idx)
            continue
        if i.startswith('/*'):
            remove.append(idx)
            continue
        if i == '\n':
            remove.append(idx)
            continue
        if i.startswith('\t\t\t\t\t'):
            remove.append(idx)
            continue
        lines[idx] = i
        
    lines = remove_index(lines,remove)
    

    structs = {}
    typedefs = {}
    
    #typedefs
    remove=[]
    for idx,i in enumerate(lines):
        if 'typedef' in i and 'struct'  not in i and 'union' not in i:
            x = i.split()
            typedefs[x[2].replace(';','')] = x[1]
            remove.append(idx)
    
    lines = remove_index(lines,remove)
    
    c2struct = {'uint16_t':'H',
                'uint32_t':'I',
                'uint64_t':'Q',
                'int16_t':'h',
                'int32_t':'i',
                'int64_t':'q'}
       
    for k,v in typedefs.items():
        if v in typedefs:
            typedefs[k] = typedefs[v]
    
    for k,v in typedefs.items():
        typedefs[k] = c2struct[v]
    
    typedefs['unsignedchar'] = 'B'
    
    
    remove=[]
    #defines:
    defines = {}
    for idx,i in enumerate(lines):
        if '#define' in i:
            x = i.split()
            tag = x[1].split('_')
            d = defines
            for i in tag:
                if not i in d:
                    d[i] = {}
                d = d[i]
            
            if x[2].isnumeric():
                x[2] = int(x[2])
            else:
                try:
                    x[2] = int(x[2],base=16)
                except ValueError:
                    pass
            d[i] = x[2]
            remove.append(idx)
            
                
    def cleanup(d):
        for k,v in d.items():
            if isinstance(v,dict):
                if len(v)==1 and k in v:
                    d[k] = v[k]
                else:
                    d[k] = cleanup(v)
        return d
    
    for k,v in defines.items():
        defines[k] = cleanup(v)
    
    defines = elfdefines(defines)
    
    lines = remove_index(lines,remove)
    
    idx = 0
    allstructs = []
    while True:
        
        try:
            i = lines[idx]
        except IndexError:
            break
        if 'typedef struct' in i:
            jdx = idx
            temp = []
            while True:
                j = lines[jdx]
                temp.append(j)
                if j.startswith('} Elf'):
                    break
                jdx = jdx + 1
            idx = jdx
            allstructs.append(temp)
        idx = idx + 1
    
    structs = {}
    for i in allstructs:
        a = False
        for j in i:
            if 'union' in j:
                a = True
        if a:
            continue
        
        name = i[-1].replace(';','').replace('} ','')
        structs[name] = {}
        for j in i[2:-1]:
            j = j.replace('unsigned char','unsignedchar')
            jj = j.split()
            t = jj[0].replace(';','')
            n = jj[1].replace(';','')
            if n.startswith('*/') or ('*/' in j and '/*' not in j):
                continue
            if '[' in n:
                s = n[n.index('[')+1:n.index(']')]
                n = n[:n.index('[')]
                if not s.isnumeric():
                    s = int(defines.find_value(s).replace('(','').replace(')',''))
                t = typedefs[t] * int(s)
            else:
                t = typedefs[t]
                
                
            # except ValueError:
                # s = '1'
            # if s.isnumeric():
                # s = int(s)
            # else:
                # s = int(defines.find_value(s).replace('(','').replace(')',''))
                # if t == 'unsignedchar':
                    # s = s//4
            structs[name][n]  = t
    
    allstructs = {}
    allstructs['generic'] = {}
    allstructs['x32'] = {}
    allstructs['x64'] = {}
    
    for i in structs:
        if 'Elf32' in i:
            allstructs['x32'][i.replace('Elf32_','')] = elfstruct(structs[i])
        elif 'Elf64' in i:
            allstructs['x64'][i.replace('Elf64_','')] = elfstruct(structs[i])
        else:
            allstructs['generic'][i] = elfstruct(structs[i])
            
    return allstructs, defines

x,y=processElfHeader()    
    
# y.find_value('EI_NIDENT')
# y.find_key('R_AARCH64_MOVW_SABS',272)
# y.find_value('ET_HIPROC')


