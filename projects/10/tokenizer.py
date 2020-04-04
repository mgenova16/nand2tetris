from .util import clean_line
from .util import is_valid_identifier
from .util import KEYWORDS
from .util import MIN_INT
from .util import MAX_INT
from .util import SYMS
from .util import Tokens


class Tokenizer:
    def __init__(self, jack_file):
        self.jack_file = jack_file
        self.jack = self.read_jack()
        self.pos = -1
        self.len = len(self.jack) - 1
        self.token = None
        self.token_type = None

    def read_jack(self):
        with open(self.jack_file, 'r') as f:
            lines = f.readlines()

        return ' '.join(clean_line(l) for l in lines)

    def has_more_tokens(self):
        return self.pos < self.len

    def advance(self):
        self.skip_whitespace()
        token = self.cur_char
        self.pos += 1
        if token == '"':
            while self.cur_char != '"':
                token += self.cur_char
                self.pos += 1
            token += self.cur_char
            self.pos += 1
        elif token not in SYMS:
            while not (self.cur_char in SYMS or self.cur_char.isspace()):
                token += self.cur_char
                self.pos += 1

        self.validate_and_set_token(token)

    def validate_and_set_token(self, token):
        if token in SYMS:
            self.token = token
            self.token_type = Tokens.SYMBOL
        elif token in KEYWORDS:
            self.token = token
            self.token_type = Tokens.KEYWORD
        elif token.isdigit():
            if not MIN_INT <= int(token) <= MAX_INT:
                print(f'Integer Over/Underflow: {token}')
                raise SystemExit
            self.token = token
            self.token_type = Tokens.INTEGER_CONST
        elif token.startswith('"') and token.endswith('"'):
            self.token = token
            self.token_type = Tokens.STRING_CONST
        elif is_valid_identifier(token):
            self.token = token
            self.token_type = Tokens.IDENTIFIER
        else:
            print(f'Invalid token: {token}')
            raise SystemExit

    def skip_whitespace(self):
        while self.pos < self.len and self.cur_char.isspace():
            self.pos += 1

    @property
    def cur_char(self):
        return self.jack[self.pos + 1]
