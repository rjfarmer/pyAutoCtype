import readelf


r = readelf.ReadElf('../test/libtester.so')

z=r._dump_debug_info2()
