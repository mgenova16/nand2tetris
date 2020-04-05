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
            self.token = Token(token, Tokens.SYMBOL)
        elif token in KEYWORDS:
            self.token = Token(token, Tokens.KEYWORD)
        elif token.isdigit():
            if not MIN_INT <= int(token) <= MAX_INT:
                print(f'Integer Over/Underflow: {token}')
                raise SystemExit
            self.token = Token(token, Tokens.INTEGER_CONST)
        elif token.startswith('"') and token.endswith('"'):
            self.token = Token(token[1:-1], Tokens.STRING_CONST)
        elif is_valid_identifier(token):
            self.token = Token(token, Tokens.IDENTIFIER)
        else:
            print(f'Invalid token: {token}')
            raise SystemExit

    def skip_whitespace(self):
        while self.pos < self.len and self.cur_char.isspace():
            self.pos += 1

    @property
    def cur_char(self):
        return self.jack[self.pos + 1]

    @property
    def token_type(self):
        return self.token.token_type

    @property
    def keyword(self):
        if self.token_type == Tokens.KEYWORD:
            return self.token.token
        else:
            print(f'ERROR: Token type {self.token_type} has no keyword')
            raise SystemExit

    @property
    def identifier(self):
        if self.token_type == Tokens.IDENTIFIER:
            return self.token.token
        else:
            print(f'ERROR: Token type {self.token_type} has no identifier')
            raise SystemExit

    @property
    def symbol(self):
        if self.token_type == Tokens.SYMBOL:
            return self.token.token
        else:
            print(f'ERROR: Token type {self.token_type} has no symbol')
            raise SystemExit

    @property
    def int_val(self):
        if self.token_type == Tokens.INTEGER_CONST:
            return self.token.token
        else:
            print(f'ERROR: Token type {self.token_type} has no integer value')
            raise SystemExit

    @property
    def string_val(self):
        if self.token_type == Tokens.STRING_CONST:
            return self.token.token
        else:
            print(f'ERROR: Token type {self.token_type} has no string value')
            raise SystemExit

    def lookahead(self, n_tokens=1):
        old_pos = self.pos
        old_token = self.token
        for _ in range(n_tokens):
            self.advance()

        token = self.token
        self.pos = old_pos
        self.token = old_token
        return token

    def __iter__(self):
        while self.has_more_tokens():
            self.advance()
            yield self.token


class Token:
    def __init__(self, token, token_type):
        self.token = token
        self.token_type = token_type

    def bad_xml(self):
        t = self.token
        if t in XML_ESCAPE:
            t = XML_ESCAPE[t]
        ttype = self.token_type.value
        return f'<{ttype}> {t} </{ttype}>\n'
