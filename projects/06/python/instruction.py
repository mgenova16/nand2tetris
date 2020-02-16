from .helper import DEST
from .helper import JUMP
from .helper import COMP_MAP
from .helper import ALLOWED_SYM_CHARS
from .helper import dec_to_bin


class Instruction():

    def __init__(self, line):
        self.line = line

        self.is_A_command = False
        self.is_C_command = False
        self.is_L_command = False
        self.is_comment = False

        self.symbol = None
        self.dest = None
        self.comp = None
        self.jump = None

        self.symbol_bin = None
        self.dest_bin = None
        self.comp_bin = None
        self.jump_bin = None

    def parse(self):
        self._sanitize_line()
        self._parse_line()

    def _sanitize_line(self):
        self.line = self.line.split('//')[0]
        self.line = self.line.strip()
        self.line = self.line.replace(' ', '')
        self.line = self.line.replace('\t', '')

    def _parse_line(self):
        if self.line == '':
            self.is_comment = True

        elif self.line.startswith('@'):
            self.is_A_command = True
            self._parse_A_command()

        elif self.line.startswith('('):
            self.is_L_command = True
            self._parse_L_command()

        else:
            self.is_C_command = True
            self._parse_C_command()

    def _parse_A_command(self):
        sym_chars = set(self.line[1:])
        assert len(sym_chars - ALLOWED_SYM_CHARS) == 0
        self.symbol = self.line[1:]
        try:
            int(self.symbol)  # if 'symbol' is a constant, convert to binary
            self.symbol_bin = dec_to_bin(int(self.symbol))
        except ValueError:
            pass

    def _parse_C_command(self):
            assert self.line.count('=') <= 1
            assert self.line.count(';') <= 1

            if '=' in self.line:
                self.dest = self.line.split('=')[0]
                assert self.dest in DEST
            if ';' in self.line:
                self.jump = self.line.split(';')[1]
                assert self.jump in JUMP

            assert self.dest is not None or self.jump is not None

            self.comp = self.line
            if self.dest is not None:
                self.comp = self.comp.split('=')[1]
            if self.jump is not None:
                self.comp = self.comp.split(';')[0]

            self.dest_bin = dec_to_bin(DEST.index(self.dest), '#05b')
            self.comp_bin = COMP_MAP[self.comp]
            self.jump_bin = dec_to_bin(JUMP.index(self.jump), '#05b')

    def _parse_L_command(self):
        assert self.line.endswith(')')
        sym_chars = set(self.line[1:-1])
        assert len(sym_chars - ALLOWED_SYM_CHARS) == 0
        self.symbol = self.line[1:-1]
