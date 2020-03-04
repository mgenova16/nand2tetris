from .command import ComparisonCommand
from .command import MathCommand
from .command import PopCommand
from .command import PushCommand
from .command import GoToCommand
from .command import IfGoToCommand
from .command import LabelCommand

from .vm import CMD_GOTO
from .vm import CMD_IF_GOTO
from .vm import CMD_LABEL
from .vm import CMD_POP
from .vm import CMD_PUSH
from .vm import CMDS_COMP
from .vm import CMDS_MATH


class Parser():

    command_type_lookup = {
        **dict.fromkeys(CMDS_MATH, MathCommand),
        **dict.fromkeys(CMDS_COMP, ComparisonCommand),
        CMD_PUSH: PushCommand,
        CMD_POP: PopCommand,
        CMD_LABEL: LabelCommand,
        CMD_GOTO: GoToCommand,
        CMD_IF_GOTO: IfGoToCommand,
    }

    def __init__(self, in_file, out_file):
        self.filename = in_file
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
            translator = command(self.filename.stem, cmd, *args)
            translator.translate()
            self.write(translator.assembly)

    def write(self, assembly):
        self.out_file.write("\n".join(assembly))
        self.out_file.write("\n")
