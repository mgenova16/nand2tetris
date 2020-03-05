from .command import CallCommand
from .command import ComparisonCommand
from .command import FunctionCommand
from .command import MathCommand
from .command import PopCommand
from .command import ProgramFlowCommand
from .command import PushCommand
from .command import ReturnCommand
from .vm import CMD_CALL
from .vm import CMD_FUNCTION
from .vm import CMD_POP
from .vm import CMD_PUSH
from .vm import CMD_RETURN
from .vm import CMDS_COMP
from .vm import CMDS_FLOW
from .vm import CMDS_MATH


class Parser:

    command_type_lookup = {
        **dict.fromkeys(CMDS_COMP, ComparisonCommand),
        **dict.fromkeys(CMDS_FLOW, ProgramFlowCommand),
        **dict.fromkeys(CMDS_MATH, MathCommand),
        CMD_POP: PopCommand,
        CMD_PUSH: PushCommand,
        CMD_CALL: CallCommand,
        CMD_FUNCTION: FunctionCommand,
        CMD_RETURN: ReturnCommand,
    }

    def __init__(self, in_file, out_file):
        self.filename = in_file.stem
        self.in_file = open(in_file, 'r')
        self.out_file = out_file

    def __del__(self):
        self.in_file.close()

    def parse(self):
        for line in self.in_file:
            cmd, *args = line.split('//')[0].strip().split(' ')
            if cmd == '':
                continue
            command = self.__class__.command_type_lookup[cmd]
            translator = command(cmd, self.filename, *args)
            translator.translate()
            self.out_file.write(f'\n//{cmd} {args}\n')
            self.write(translator.assembly)

    def write(self, assembly):
        self.out_file.write('\n'.join(assembly) + '\n')
