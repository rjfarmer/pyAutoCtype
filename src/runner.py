import readelf

r = readelf.ReadElf('../test/libtester.so')

z = r.getDebugInfo()
#needs to get macros
