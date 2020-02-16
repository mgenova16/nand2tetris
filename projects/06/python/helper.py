def dec_to_bin(val, f='#018b'):
    return format(val, f)[2:]


def sym_table():
    s = {
        'SP': 0,
        'LCL': 1,
        'ARG': 2,
        'THIS': 3,
        'THAT': 4,
        'SCREEN': 16384,
        'KBD': 24576,
        **{'R{}'.format(i): i for i in range(16)},
    }
    return s


DEST = [None, 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD']
JUMP = [None, 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP']

COMP_MAP = {
    '0':   '0101010', '1':   '0111111', '-1':  '0111010', 'D':   '0001100',
    'A':   '0110000', '!D':  '0001101', '!A':  '0110001', '-D':  '0001111',
    '-A':  '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
    'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
    'D&A': '0000000', 'D|A': '0010101', 'M':   '1110000', '!M':  '1110001',
    '-M':  '1110011', 'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
    'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000', 'D|M': '1010101',
}

ALLOWED_SYM_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890._:$')
