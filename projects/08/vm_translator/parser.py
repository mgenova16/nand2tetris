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
from .vm import COMPARISON_COMMANDS
from .vm import MATH_COMMANDS
from .vm import PROGRAM_FLOW_COMMANDS


class Parser:

    command_type_lookup = {
        **dict.fromkeys(COMPARISON_COMMANDS, ComparisonCommand),
        **dict.fromkeys(PROGRAM_FLOW_COMMANDS, ProgramFlowCommand),
        **dict.fromkeys(MATH_COMMANDS, MathCommand),
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
            c_type = self.__class__.command_type_lookup[cmd]
            command = c_type(cmd, self.filename, *args)
            command.translate()
            self.write(command.assembly)

    def write(self, assembly):
        self.out_file.write('\n'.join(assembly) + '\n')
