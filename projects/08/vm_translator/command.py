from .vm import FRAME_ADDRS


class MathCommand():

    ops = {
        'add': {'asm_op': ['M=M+D'], 'n_args': 2},
        'sub': {'asm_op': ['M=M-D'], 'n_args': 2},
        'neg': {'asm_op':  ['M=-M'], 'n_args': 1},
        'and': {'asm_op': ['M=M&D'], 'n_args': 2},
        'or':  {'asm_op': ['M=M|D'], 'n_args': 2},
        'not': {'asm_op':  ['M=!M'], 'n_args': 1},
    }

    def __init__(self, filename, operation):
        self.operation = self.__class__.ops[operation]['asm_op']
        self.n_args = self.__class__.ops[operation]['n_args']
        self.assembly = []

    def translate(self):
        if self.n_args == 1:
            self.assembly += ['@SP', 'A=M-1']
        else:
            self.assembly += ['@SP', 'AM=M-1', 'D=M', 'A=A-1']
        self.assembly += self.operation


class ComparisonCommand:

    ops = {'eq': 'D;JEQ', 'lt': 'D;JLT', 'gt': 'D;JGT'}

    def comp_incrementer():
        i = 0
        while True:
            yield i
            i += 1

    comp_counter = comp_incrementer()

    def __init__(self, filename, operation):
        self.assembly = []
        self.operation = self.__class__.ops[operation]

    def translate(self):
        comp_count = next(self.__class__.comp_counter)
        self.assembly += ['@SP', 'AM=M-1', 'D=M']
        self.assembly += ['@SP', 'A=M-1']
        self.assembly += ['D=M-D']
        self.assembly += [f'@COMP_JUMP.{comp_count}']
        self.assembly += [self.operation]
        self.assembly += ['@SP', 'A=M-1', 'M=0']
        self.assembly += [f'@CONTINUE_JUMP.{comp_count}']
        self.assembly += ['0;JMP']
        self.assembly += [f'(COMP_JUMP.{comp_count})']
        self.assembly += ['@SP', 'A=M-1', 'M=-1']
        self.assembly += [f'(CONTINUE_JUMP.{comp_count})']


class MemoryCommand:

    def __init__(self, filename, segment, index):
        self.segment = segment
        self.index = index
        self.filename = filename
        self.assembly = []
        self.seg_addr = self.get_segment_address()

    def get_segment_address(self):
        i = int(self.index)
        if self.segment in FRAME_ADDRS:
            address = FRAME_ADDRS[self.segment]
            if i == 0:
                return [address, 'A=M']
            else:
                return [address, 'D=M', f'@{self.index}', 'A=D+A']
        elif self.segment == 'pointer':
            assert 0 <= i <= 1, f'Invalid index for pointer: {i}'
            return [f'@R{3 + i}']
        elif self.segment == 'temp':
            assert 0 <= i <= 7, f'Invalid index for temp: {i}'
            return [f'@R{5 + i}']
        elif self.segment == 'static':
            return [f'@{self.filename}.{self.index}']
        elif self.segment == 'constant':
            return [f'@{self.index}']


class PushCommand(MemoryCommand):

    def __init__(self, filename, operation, segment, index):
        super().__init__(filename, segment, index)

    def translate(self):
        self.assembly += self.seg_addr
        self.assembly += ['D=A'] if self.segment == 'constant' else ['D=M']
        self.assembly += ['@SP', 'M=M+1', 'A=M-1', 'M=D']


class PopCommand(MemoryCommand):

    def __init__(self, filename, operation, segment, index):
        super().__init__(filename, segment, index)

    def translate(self):
        if len(self.seg_addr) > 1:
            self.assembly += self.seg_addr
            self.assembly += ['D=A']
            self.assembly += ['@R13', 'M=D']
            self.assembly += ['@SP', 'AM=M-1', 'D=M']
            self.assembly += ['@R13', 'A=M', 'M=D']
        else:
            self.assembly += ['@SP', 'AM=M-1', 'D=M']
            self.assembly += self.seg_addr
            self.assembly += ['M=D']


class LabelCommand:

    def __init__(self, filename, operation, label):
        self.filename = filename
        self.label = label
        self.assembly = []

    def translate(self):
        self.assembly += [f'({self.filename}${self.label})']


class GoToCommand:

    def __init__(self, filename, operation, label):
        self.filename = filename
        self.label = label
        self.assembly = []

    def translate(self):
        self.assembly += [f'@{self.filename}${self.label}']
        self.assembly += ['0;JMP']


class IfGoToCommand:

    def __init__(self, filename, operation, label):
        self.filename = filename
        self.label = label
        self.assembly = []

    def translate(self):
        self.assembly += ['@SP', 'AM=M-1', 'D=M']
        self.assembly += [f'@{self.filename}${self.label}']
        self.assembly += ['D;JNE']
