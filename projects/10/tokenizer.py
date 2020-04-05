from .util import clean_line
from .util import is_valid_identifier
from .util import KEYWORDS
from .util import MIN_INT
from .util import MAX_INT
from .util import strip_multiline_comments
from .util import SYMS
from .util import Tokens
from .util import XML_ESCAPE


class Tokenizer:
    def __init__(self, jack_fh):
        self.jack_fh = jack_fh
        self.jack = self.read_jack()
        self.pos = -1
        self.len = len(self.jack) - 1
        self.token = None
        self.token_type = None

    def read_jack(self):
        lines = self.jack_fh.readlines()
        jack = ' '.join(clean_line(l) for l in lines)
        return strip_multiline_comments(jack)

    def has_more_tokens(self):
        self.skip_whitespace()
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
            self.token = token[1:-1]
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

    def lookahead(self, n_char):
        if self.pos + n_char < self.len:
            return self.jack[self.pos + n_char + 1]
        else:
            return None

    def __str__(self):
        token_type = self.token_type.value
        token = self.token
        if token in XML_ESCAPE:
            token = XML_ESCAPE[token]
        return f'<{token_type}> {token} </{token_type}>'
