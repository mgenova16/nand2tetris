from .tokenizer import Tokenizer
from .util import KEYWORD_CONSTS
from .util import Tokens
from .util import TYPE_CONSTS
from .util import UNARY_OPS


class CompilationEngine:

    def __init__(self, f_in, f_out):
        self.f_name = f_in.stem
        self.f_in = open(f_in, 'r')
        self.f_out = open(f_out, 'w')
        self.tokenizer = Tokenizer(self.f_in)
        self.stack = []
        self.indent_str = '  '

    def __del__(self):
        self.f_in.close()
        self.f_out.close()

    def tokenize(self):
        self.f_out.write('<tokens>\n')
        for token in self.tokenizer:
            self.f_out.write(f'{token.bad_xml()}')
        self.f_out.write('</tokens>\n')

    def start_sub_compilation_unit(self, unit):
        self.stack.append(unit)
        self.write_badxml_open()

    def end_sub_compilation_unit(self, unit):
        self.write_badxml_close()
        assert self.stack.pop() == unit

    def expect_and_write(self, tokens):
        if not isinstance(tokens, list):
            tokens = [tokens]

        self.tokenizer.advance()
        actual_token = self.tokenizer.token_value
        if actual_token not in tokens:
            print(f'ERROR: Expected {"|".join(tokens)} but got {actual_token}')
            raise SystemExit

        self.write_badxml()

    def validate_and_write_identifier(self):
        self.tokenizer.advance()
        if not self.tokenizer.token_type == Tokens.IDENTIFIER:
            print(f'Invalid Identifier: {self.tokenizer.token_value}')
            raise SystemExit
        self.write_badxml()

    def validate_and_write_function_type(self):
        self.tokenizer.advance()
        # easy to validate built-ins, how to validate custom classes?
        self.write_badxml()

    def validate_and_write_variable_type(self):
        self.tokenizer.advance()
        # easy to validate build-ins, how to validate custom classes?
        self.write_badxml()

    def compile(self):
        self.compile_class()

    def compile_class(self):
        compilation_unit = 'class'
        self.start_sub_compilation_unit(compilation_unit)

        self.expect_and_write('class')
        self.expect_and_write(self.f_name)
        self.expect_and_write('{')

        self.compile_class_var_decs()
        self.compile_subroutine_decs()
        self.expect_and_write('}')

        self.end_sub_compilation_unit(compilation_unit)

    def compile_class_var_decs(self):
        compilation_unit = 'classVarDec'
        possible_fields = ['static', 'field']
        next_token = self.tokenizer.lookahead()

        while next_token.token in possible_fields:
            self.start_sub_compilation_unit(compilation_unit)
            self.expect_and_write(possible_fields)
            self.validate_and_write_variable_type()
            self.validate_and_write_identifier()
            next_token = self.tokenizer.lookahead()
            while next_token.token == ',':
                self.expect_and_write(',')
                self.validate_and_write_identifier()
                next_token = self.tokenizer.lookahead()
            self.expect_and_write(';')
            self.end_sub_compilation_unit(compilation_unit)
            next_token = self.tokenizer.lookahead()

    def compile_subroutine_decs(self):
        compilation_unit = 'subroutineDec'
        possible_fields = ['constructor', 'function', 'method']
        next_token = self.tokenizer.lookahead()
        while next_token.token in possible_fields:
            self.start_sub_compilation_unit(compilation_unit)
            self.expect_and_write(possible_fields)
            self.validate_and_write_function_type()
            self.validate_and_write_identifier()
            self.expect_and_write('(')
            self.compile_parameter_list()
            self.expect_and_write(')')
            self.compile_subroutine_body()
            self.end_sub_compilation_unit(compilation_unit)
            next_token = self.tokenizer.lookahead()

    def compile_parameter_list(self):
        compilation_unit = 'parameterList'
        self.start_sub_compilation_unit(compilation_unit)
        next_token = self.tokenizer.lookahead()

        while next_token.token != ')':
            if next_token.token == ',':
                self.expect_and_write(',')
            self.validate_and_write_variable_type()
            self.validate_and_write_identifier()
            next_token = self.tokenizer.lookahead()

        self.end_sub_compilation_unit(compilation_unit)

    def compile_subroutine_body(self):
        compilation_unit = 'subroutineBody'
        self.start_sub_compilation_unit(compilation_unit)

        self.expect_and_write('{')
        self.compile_var_decs()
        self.compile_statements()
        self.expect_and_write('}')

        self.end_sub_compilation_unit(compilation_unit)

    def compile_var_decs(self):
        compilation_unit = 'varDec'

        next_token = self.tokenizer.lookahead()
        while next_token.token == 'var':
            self.start_sub_compilation_unit(compilation_unit)
            self.expect_and_write('var')
            self.validate_and_write_variable_type()
            self.validate_and_write_identifier()
            next_token = self.tokenizer.lookahead()
            while next_token.token == ',':
                self.expect_and_write(',')
                self.validate_and_write_identifier()
                next_token = self.tokenizer.lookahead()
            self.expect_and_write(';')
            self.end_sub_compilation_unit(compilation_unit)
            next_token = self.tokenizer.lookahead()

    def compile_statements(self):
        compilation_unit = 'statements'
        self.start_sub_compilation_unit(compilation_unit)

        next_token = self.tokenizer.lookahead()
        while next_token.token != '}':
            self.compile_statement()
            next_token = self.tokenizer.lookahead()

        self.end_sub_compilation_unit(compilation_unit)

    def compile_statement(self):
        next_token = self.tokenizer.lookahead()
        if next_token.token == 'let':
            self.compile_let_statement()
        elif next_token.token == 'if':
            self.compile_if_statement()
        elif next_token.token == 'while':
            self.compile_while_statement()
        elif next_token.token == 'do':
            self.compile_do_statement()
        elif next_token.token == 'return':
            self.compile_return_statement()
        else:
            print(f'ERROR: Expected statement, got {next_token.token}')
            raise SystemExit

    def compile_let_statement(self):
        compilation_unit = 'letStatement'
        self.start_sub_compilation_unit(compilation_unit)

        self.expect_and_write('let')
        self.validate_and_write_identifier()
        next_token = self.tokenizer.lookahead()
        if next_token.token == '[':
            self.expect_and_write('[')
            self.compile_expression()
            self.expect_and_write(']')
        self.expect_and_write('=')
        self.compile_expression()
        self.expect_and_write(';')

        self.end_sub_compilation_unit(compilation_unit)

    def compile_if_statement(self):
        compilation_unit = 'ifStatement'
        self.start_sub_compilation_unit(compilation_unit)

        self.expect_and_write('if')
        self.expect_and_write('(')
        self.compile_expression()
        self.expect_and_write(')')
        self.expect_and_write('{')
        self.compile_statements()
        self.expect_and_write('}')

        next_token = self.tokenizer.lookahead()
        if next_token.token == 'else':
            self.expect_and_write('else')
            self.expect_and_write('{')
            self.compile_statements()
            self.expect_and_write('}')

        self.end_sub_compilation_unit(compilation_unit)

    def compile_while_statement(self):
        compilation_unit = 'whileStatement'
        self.start_sub_compilation_unit(compilation_unit)

        self.expect_and_write('while')
        self.expect_and_write('(')
        self.compile_expression()
        self.expect_and_write(')')
        self.expect_and_write('{')
        self.compile_statements()
        self.expect_and_write('}')

        self.end_sub_compilation_unit(compilation_unit)

    def compile_do_statement(self):
        compilation_unit = 'doStatement'
        self.start_sub_compilation_unit(compilation_unit)

        self.expect_and_write('do')
        self.compile_subroutine_call()
        self.expect_and_write(';')

        self.end_sub_compilation_unit(compilation_unit)

    def compile_return_statement(self):
        compilation_unit = 'returnStatement'
        self.start_sub_compilation_unit(compilation_unit)

        self.expect_and_write('return')

        next_token = self.tokenizer.lookahead()
        if next_token.token != ';':
            self.compile_expression()

        self.expect_and_write(';')

        self.end_sub_compilation_unit(compilation_unit)

    def compile_subroutine_call(self):
        self.validate_and_write_identifier()

        next_token = self.tokenizer.lookahead()
        if next_token.token == '.':
            self.expect_and_write('.')
            self.validate_and_write_identifier()

        self.expect_and_write('(')
        self.compile_expression_list()
        self.expect_and_write(')')

    def compile_expression_list(self):
        compilation_unit = 'expressionList'
        self.start_sub_compilation_unit(compilation_unit)

        next_token = self.tokenizer.lookahead()
        while next_token.token != ')':
            if next_token.token == ',':
                self.expect_and_write(',')
            self.compile_expression()
            next_token = self.tokenizer.lookahead()

        self.end_sub_compilation_unit(compilation_unit)

    def compile_expression(self):
        compilation_unit = 'expression'
        self.start_sub_compilation_unit(compilation_unit)
        self.compile_term()

        next_token = self.tokenizer.lookahead()
        while next_token.token in list('+-*/&|<>='):
            self.expect_and_write(next_token.token)
            self.compile_term()
            next_token = self.tokenizer.lookahead()

        self.end_sub_compilation_unit(compilation_unit)

    def compile_term(self):
        compilation_unit = 'term'
        self.start_sub_compilation_unit(compilation_unit)

        next_token = self.tokenizer.lookahead()
        ttype = next_token.token_type
        token = next_token.token
        if ttype in TYPE_CONSTS or token in KEYWORD_CONSTS:
            self.expect_and_write(token)
        elif token == '(':
            self.expect_and_write('(')
            self.compile_expression()
            self.expect_and_write(')')
        elif token in UNARY_OPS:
            self.expect_and_write(token)
            self.compile_term()
        else:
            next_next_token = self.tokenizer.lookahead(2)
            if next_next_token.token in ['(', '.']:
                self.compile_subroutine_call()
            elif next_next_token.token == '[':
                self.validate_and_write_identifier()
                self.expect_and_write('[')
                self.compile_expression()
                self.expect_and_write(']')
            else:
                self.validate_and_write_identifier()

        self.end_sub_compilation_unit(compilation_unit)

    def write_badxml(self):
        s = f'{self.indent}{self.tokenizer.token.bad_xml()}'
        self.f_out.write(s)

    def write_badxml_open(self):
        s = f'{self.indent_open_close}<{self.stack[-1]}>\n'
        self.f_out.write(s)

    def write_badxml_close(self):
        s = f'{self.indent_open_close}</{self.stack[-1]}>\n'
        self.f_out.write(s)

    @property
    def indent(self):
        return self.indent_str * len(self.stack)

    @property
    def indent_open_close(self):
        return self.indent_str * (len(self.stack) - 1)
