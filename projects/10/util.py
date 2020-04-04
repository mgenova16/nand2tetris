from enum import auto
from enum import Enum

MIN_INT = 0
MAX_INT = 2**16 - 1
OPEN_COMMENT = '/*'
CLOSE_COMMENT = '*/'
COMMENT_START = '//'

SYMS = list('{}()[].,;+-*/&|<>=~')
KEYWORDS = [
    'class', 'constructor', 'function', 'method',
    'field', 'static', 'var', 'int', 'char', 'boolean',
    'void', 'true', 'false', 'null', 'this', 'let',
    'do', 'if', 'else', 'while', 'return'
]


def clean_line(line):
    line = line.split(COMMENT_START)[0].strip()
    if OPEN_COMMENT in line and CLOSE_COMMENT in line:
        start_comment = line.find(OPEN_COMMENT)
        end_comment = line.find(CLOSE_COMMENT) + 2
        line = line[:start_comment] + line[end_comment:]
        line = line.strip()
    return line


def is_valid_identifier(token):
    if not (token[0].isalpha() or token[0] == '_'):
        return False
    for c in token:
        if not (c.isalnum() or c == '_'):
            return False
    return True


class EnumAutoName(Enum):
    def _generate_next_value_(name, start, count, last):
        return name


class Tokens(EnumAutoName):
    IDENTIFIER = auto()
    INTEGER_CONST = auto()
    KEYWORD = auto()
    STRING_CONST = auto()
    SYMBOL = auto()
