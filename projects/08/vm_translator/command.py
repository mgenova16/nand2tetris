from .vm import CMD_ADD
from .vm import CMD_SUB
from .vm import CMD_NEG
from .vm import CMD_AND
from .vm import CMD_OR
from .vm import CMD_NOT
from .vm import CMD_EQ
from .vm import CMD_LT
from .vm import CMD_GT
from .vm import CMD_LABEL
from .vm import CMD_GOTO
from .vm import CMD_IF_GOTO
from .vm import FRAME_ADDRS


class Command:

    def __init__(self, operation, **kwargs):
        self.operation = operation
        self.__dict__.update(**kwargs)
        self.assembly = []

    def __repr__(self):
        return '\n'.join(self.assembly) + '\n'


class MathCommand(Command):

    ops = {
        CMD_ADD: {'asm': ['M=M+D'], 'n_args': 2},
        CMD_SUB: {'asm': ['M=M-D'], 'n_args': 2},
        CMD_NEG: {'asm':  ['M=-M'], 'n_args': 1},
        CMD_AND: {'asm': ['M=M&D'], 'n_args': 2},
        CMD_OR:  {'asm': ['M=M|D'], 'n_args': 2},
        CMD_NOT: {'asm':  ['M=!M'], 'n_args': 1},
    }

    def __init__(self, operation, *args):
        super().__init__(operation)
        self.operation = self.__class__.ops[operation]['asm']
        self.n_args = self.__class__.ops[operation]['n_args']

    def translate(self):
        if self.n_args == 1:
            self.assembly += ['@SP', 'A=M-1']
        else:
            self.assembly += ['@SP', 'AM=M-1', 'D=M', 'A=A-1']
        self.assembly += self.operation


class ComparisonCommand(Command):

    ops = {CMD_EQ: ['D;JEQ'], CMD_LT: ['D;JLT'], CMD_GT: ['D;JGT']}

    def comp_incrementer():
        i = 0
        while True:
            yield i
            i += 1

    comp_counter = comp_incrementer()

    def __init__(self, operation, *args):
        super().__init__(operation)
        self.operation = self.__class__.ops[self.operation]

    def translate(self):
        comp_count = next(self.__class__.comp_counter)
        self.assembly += ['@SP', 'AM=M-1', 'D=M']
        self.assembly += ['@SP', 'A=M-1']
        self.assembly += ['D=M-D']
        self.assembly += [f'@COMP_JUMP.{comp_count}']
        self.assembly += self.operation
        self.assembly += ['@SP', 'A=M-1', 'M=0']
        self.assembly += [f'@CONTINUE_JUMP.{comp_count}']
        self.assembly += ['0;JMP']
        self.assembly += [f'(COMP_JUMP.{comp_count})']
        self.assembly += ['@SP', 'A=M-1', 'M=-1']
        self.assembly += [f'(CONTINUE_JUMP.{comp_count})']


class MemoryCommand(Command):

    def __init__(self, operation, filename, segment, index):
        kwargs = {'filename': filename, 'segment': segment, 'index': index}
        super().__init__(operation, **kwargs)
        self.seg_addr = self.get_segment_address()

    def get_segment_address(self):
        i = int(self.index)
        if self.segment in FRAME_ADDRS:
            address = FRAME_ADDRS[self.segment]
            if i == 0:
                return [address, 'A=M']
            else:
                return [address, 'D=M', f'@{i}', 'A=D+A']
        elif self.segment == 'pointer':
            assert 0 <= i <= 1, f'Invalid index for pointer: {i}'
            return [f'@R{3 + i}']
        elif self.segment == 'temp':
            assert 0 <= i <= 7, f'Invalid index for temp: {i}'
            return [f'@R{5 + i}']
        elif self.segment == 'static':
            return [f'@{self.filename}.{i}']
        elif self.segment == 'constant':
            return [f'@{i}']
        else:
            raise SystemExit(f'Invalid segment: {self.segment}')


class PopCommand(MemoryCommand):

    def __init__(self, operation, filename, segment, index):
        super().__init__(operation, filename, segment, index)

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


class PushCommand(MemoryCommand):

    def __init__(self, operation, filename, segment, index):
        super().__init__(operation, filename, segment, index)

    def translate(self):
        self.assembly += self.seg_addr
        self.assembly += ['D=A'] if self.segment == 'constant' else ['D=M']
        self.assembly += ['@SP', 'M=M+1', 'A=M-1', 'M=D']


class ProgramFlowCommand(Command):

    formatters = {
        CMD_LABEL: '({}${})',
        CMD_GOTO: '@{}${}',
        CMD_IF_GOTO: '@{}${}',
    }

    def __init__(self, operation, filename, label, *args):
        super().__init__(operation, filename=filename, label=label)
        unformatted = self.__class__.formatters[self.operation]
        self.formatted_label = [unformatted.format(self.filename, self.label)]

    def translate(self):
        if self.operation == CMD_IF_GOTO:
            self.assembly += ['@SP', 'AM=M-1', 'D=M']
        self.assembly += self.formatted_label
        if self.operation == CMD_IF_GOTO:
            self.assembly += ['D;JNE']
        elif self.operation == CMD_GOTO:
            self.assembly += ['0;JMP']


class FunctionCommand(Command):

    def __init__(self, operation, filename, function_name, n):
        super().__init__(operation, function_name=function_name, n=n)

    def translate(self):
        n = int(self.n)
        self.assembly += [f'({self.function_name})']
        self.assembly += ['D=0', '@SP', 'M=M+1', 'A=M-1', 'M=D'] * n


class CallCommand(Command):

    def call_incrementer():
        i = 0
        while True:
            yield i
            i += 1

    call_count = call_incrementer()

    def __init__(self, operation, filename, function_name, n):
        super().__init__(operation, function_name=function_name, n=n)

    def translate(self):
        n = int(self.n)
        count = next(self.__class__.call_count)
        return_label = self.function_name + f'_RETURN.{count}'
        self.assembly += [f'@{return_label}']
        self.assembly += ['D=A']
        self.assembly += ['@SP', 'M=M+1', 'A=M-1', 'M=D']
        for addr in FRAME_ADDRS.values():
            self.assembly += [addr]
            self.assembly += ['D=M']
            self.assembly += ['@SP', 'M=M+1', 'A=M-1', 'M=D']

        self.assembly += ['@SP', 'D=M', '@LCL', 'M=D']
        self.assembly += [f'@{n + 5}', 'D=D-A', '@ARG', 'M=D']

        self.assembly += [f'@{self.function_name}']
        self.assembly += ['0;JMP']
        self.assembly += [f'({return_label})']


class ReturnCommand(Command):

    def __init__(self, operation, *args):
        super().__init__(operation)

    def translate(self):
        tmp_frame = 'R13'
        tmp_ret = 'R14'

        self.assembly += ['@LCL', 'D=M', f'@{tmp_frame}', 'M=D']
        self.assembly += [f'@{tmp_frame}', 'D=M']
        self.assembly += ['@5', 'A=D-A', 'D=M']
        self.assembly += [f'@{tmp_ret}', 'M=D']
        self.assembly += ['@SP', 'AM=M-1', 'D=M']
        self.assembly += ['@ARG', 'A=M', 'M=D']
        self.assembly += ['@ARG', 'D=M', '@SP', 'M=D+1']
        addrs = list(FRAME_ADDRS.values())
        addrs.reverse()
        for i, addr in enumerate(addrs):
            self.assembly += [f'@{tmp_frame}', 'D=M']
            self.assembly += [f'@{i + 1}', 'A=D-A', 'D=M']
            self.assembly += [addr, 'M=D']

        self.assembly += [f'@{tmp_ret}', 'A=M', '0;JMP']
