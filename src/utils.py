
_names = [
	'C89',#* ISO C:1989 */
    'C',#C */
    'Ada83',#* ISO Ada:1983 */
    'C_plus_plus',#ISO C++:1998 */
    'Cobol74',#* ISO Cobol:1974 */
    'Cobol85',#* ISO Cobol:1985 */
    'Fortran77',#* ISO FORTRAN 77 */
    'Fortran90',#* ISO Fortran 90 */
    'Pascal83',#* ISO Pascal:1983 */
    'Modula2',#* ISO Modula-2:1996 */
    'Java',#* Java */
    'C99',#* ISO C:1999 */
    'Ada95',#* ISO Ada:1995 */
    'Fortran95',#* ISO Fortran 95 */
    'PL1',#* ISO PL/1:1976 */
    'ObjC',#* Objective-C */
    'ObjC_plus_plus',#Objective-C++ */
    'UPC',#* Unified Parallel C */
    'D',#D */
    'Python',#* Python */
    'Go',#* Go */
    'Haskell',#* Haskell */
    'C_plus_plus_11',#ISO C++:2011 */
    'C11',#* ISO C:2011 */
    'C_plus_plus_14',#ISO C++:2014 */
    'Fortran03',#* ISO/IEC 1539-1:2004 */
    'Fortran08',#* ISO/IEC 1539-1:2010 */
	 ]
	 
_type = [
    'void', #0x0,
    'address',# 0x1,
    'boolean',# 0x2,
    'complex_float', #0x3,
    'float', #0x4,
    'signed', #0x5,
    'signed_char', #0x6,
    'unsigned', #0x7,
    'unsigned_char', #0x8,
    'imaginary_float',# 0x9,
    'packed_decimal',# 0xa,
    'numeric_string',# 0xb,
    'edited', #0xc,
    'signed_fixed', #0xd,
    'unsigned_fixed', #0xe,
    'decimal_float', #0xf,
    'UTF', #0x10,
]

def get_language(code):
	return _names[code -1].lower()
	
def get_type(code):
	return _types[code] 
	 
	 
