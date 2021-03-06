from enum import Enum


class Tokens(Enum):
    IDENTIFIER = 'identifier'
    INTEGER_CONST = 'integerConstant'
    KEYWORD = 'keyword'
    STRING_CONST = 'stringConstant'
    SYMBOL = 'symbol'


MIN_INT = 0
MAX_INT = 2**16 - 1
OPEN_COMMENT = '/*'
CLOSE_COMMENT = '*/'
COMMENT_START = '//'

XML_ESCAPE = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
}

SYMS = list('{}()[].,;+-*/&|<>=~')
UNARY_OPS = ['-', '~']

KEYWORDS = [
    'class', 'constructor', 'function', 'method',
    'field', 'static', 'var', 'int', 'char', 'boolean',
    'void', 'true', 'false', 'null', 'this', 'let',
    'do', 'if', 'else', 'while', 'return'
]

TYPES = ['int', 'char', 'boolean', 'void', 'String', 'Array']
TYPE_CONSTS = [Tokens.INTEGER_CONST, Tokens.STRING_CONST]
KEYWORD_CONSTS = ['true', 'false', 'null', 'this']

ARITHMETIC_LOOKUP = {
    '+': 'add',
    '-': 'sub',
    '~': 'not',
    '&': 'and',
    '|': 'or',
    '>': 'gt',
    '<': 'lt',
    '=': 'eq'
}

UNARY_OP_LOOKUP = {
    '~': 'not',
    '-': 'neg',
}


def get_segment(var_kind):
    if var_kind == 'field':
        return 'this'
    return var_kind


def clean_line(line):
    line = line.split(COMMENT_START)[0].strip()
    return line


def strip_multiline_comments(s):
    while OPEN_COMMENT in s and CLOSE_COMMENT in s:
        start_comment = s.find(OPEN_COMMENT)
        end_comment = s.find(CLOSE_COMMENT) + 2
        s = s[:start_comment] + s[end_comment:]
    return s.strip()


def is_valid_identifier(token):
    if not (token[0].isalpha() or token[0] == '_'):
        return False
    for c in token:
        if not (c.isalnum() or c == '_'):
            return False
    return True
