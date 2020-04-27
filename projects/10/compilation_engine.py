from .symbol_table import SymbolTable
from .tokenizer import Tokenizer
from .util import ARITHMETIC_LOOKUP
from .util import KEYWORD_CONSTS
from .util import Tokens
from .util import TYPES
from .util import UNARY_OPS
from .util import UNARY_OP_LOOKUP
from .util import get_segment
from .vm_writer import VMWriter


class CompilationEngine:

    def __init__(self, f_in, f_out, classes, debug=False):
        self.class_name = f_in.stem
        self.f_in = open(f_in, 'r')
        self.vm_writer = VMWriter(open(f_out, 'w'))
        self.tokenizer = Tokenizer(self.f_in)
        self.indent_str = '  '
        self.available_types = TYPES + classes
        self.symbol_table = SymbolTable()
        self.while_idx = -1
        self.if_idx = -1

    def __del__(self):
        self.f_in.close()
        del self.vm_writer

    def expect(self, tokens):
        if not isinstance(tokens, list):
            tokens = [tokens]

        self.tokenizer.advance()
        actual_token = self.tokenizer.token_value
        if actual_token not in tokens:
            err = f'ERROR: Expected {"|".join(tokens)} but got {actual_token}'
            raise ValueError(err)
        return actual_token

    def validate_identifier(self):
        self.tokenizer.advance()
        if not self.tokenizer.token_type == Tokens.IDENTIFIER:
            print(f'Invalid Identifier: {self.tokenizer.token_value}')
            raise SystemExit
        return self.tokenizer.token_value

    def validate_type(self):
        self.tokenizer.advance()
        if self.tokenizer.token_value not in self.available_types:
            print(f'Invalid type: {self.tokenizer.token_value}')
            raise SystemExit
        return self.tokenizer.token_value

    def compile(self):
        self.compile_class()

    def compile_class(self):
        self.expect('class')
        self.expect(self.class_name)
        self.expect('{')

        self.compile_class_var_decs()
        self.compile_subroutine_decs()
        self.expect('}')

    def compile_class_var_decs(self):
        possible_fields = ['static', 'field']
        next_token = self.tokenizer.lookahead()

        while next_token.token in possible_fields:
            kind = self.expect(possible_fields)
            var_type = self.validate_type()
            name = self.validate_identifier()
            self.symbol_table.add(name, var_type, kind)
            next_token = self.tokenizer.lookahead()
            while next_token.token == ',':
                self.expect(',')
                name = self.validate_identifier()
                self.symbol_table.add(name, var_type, kind)
                next_token = self.tokenizer.lookahead()
            self.expect(';')
            next_token = self.tokenizer.lookahead()

    def compile_subroutine_decs(self):
        possible_fields = ['constructor', 'function', 'method']
        next_token = self.tokenizer.lookahead()
        while next_token.token in possible_fields:
            self.symbol_table.enter_new_scope()
            subroutine_type = self.expect(possible_fields)
            if subroutine_type == 'method':
                self.symbol_table.add('this', self.class_name, 'argument')

            self.validate_type()
            subroutine_name = self.validate_identifier()
            function_name = f'{self.class_name}.{subroutine_name}'

            self.expect('(')
            self.compile_parameter_list()
            self.expect(')')
            self.expect('{')

            self.compile_var_decs()
            n_locals = self.symbol_table.n_locals()
            self.vm_writer.write_function(function_name, n_locals)

            if subroutine_type == 'constructor':
                num_fields = self.symbol_table.n_fields()
                self.vm_writer.write_push('constant', num_fields)
                self.vm_writer.write_call('Memory.alloc', 1)
                self.vm_writer.write_pop('pointer', 0)
            elif subroutine_type == 'method':
                self.vm_writer.write_push('argument', 0)
                self.vm_writer.write_pop('pointer', 0)

            self.compile_statements()
            self.expect('}')
            self.symbol_table.close_scope()
            next_token = self.tokenizer.lookahead()

    def compile_parameter_list(self):
        kind = 'argument'

        next_token = self.tokenizer.lookahead()

        while next_token.token != ')':
            if next_token.token == ',':
                self.expect(',')
            var_type = self.validate_type()
            name = self.validate_identifier()
            self.symbol_table.add(name, var_type, kind)
            next_token = self.tokenizer.lookahead()

    def compile_var_decs(self):
        kind = 'local'

        next_token = self.tokenizer.lookahead()
        while next_token.token == 'var':
            self.expect('var')
            var_type = self.validate_type()
            name = self.validate_identifier()
            self.symbol_table.add(name, var_type, kind)
            next_token = self.tokenizer.lookahead()
            while next_token.token == ',':
                self.expect(',')
                name = self.validate_identifier()
                self.symbol_table.add(name, var_type, kind)
                next_token = self.tokenizer.lookahead()
            self.expect(';')
            next_token = self.tokenizer.lookahead()

    def compile_statements(self):
        next_token = self.tokenizer.lookahead()
        while next_token.token != '}':
            self.compile_statement()
            next_token = self.tokenizer.lookahead()

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
        self.expect('let')
        var_name = self.validate_identifier()
        var = self.symbol_table.lookup(var_name)
        next_token = self.tokenizer.lookahead()
        if next_token.token == '[':
            self.expect('[')
            self.compile_expression()
            self.expect(']')
            self.vm_writer.write_push(get_segment(var.kind), var.idx)
            self.vm_writer.write_arithmetic('add')
            self.expect('=')
            self.compile_expression()
            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        else:
            self.expect('=')
            self.compile_expression()
            self.vm_writer.write_pop(get_segment(var.kind), var.idx)

        self.expect(';')

    def compile_if_statement(self):
        self.if_idx += 1
        idx = self.if_idx

        self.expect('if')
        self.expect('(')
        self.compile_expression()
        self.expect(')')
        self.expect('{')
        self.vm_writer.write_if(f'IF_TRUE{idx}')
        self.vm_writer.write_goto(f'IF_FALSE{idx}')
        self.vm_writer.write_label(f'IF_TRUE{idx}')
        self.compile_statements()
        self.expect('}')
        next_token = self.tokenizer.lookahead()
        if next_token.token == 'else':
            self.expect('else')
            self.expect('{')
            self.vm_writer.write_goto(f'IF_END{idx}')
            self.vm_writer.write_label(f'IF_FALSE{idx}')
            self.compile_statements()
            self.expect('}')
            self.vm_writer.write_label(f'IF_END{idx}')
        else:
            self.vm_writer.write_label(f'IF_FALSE{idx}')

    def compile_while_statement(self):
        self.while_idx += 1
        idx = self.while_idx

        self.vm_writer.write_label(f'WHILE_EXP{idx}')
        self.expect('while')
        self.expect('(')
        self.compile_expression()
        self.expect(')')
        self.expect('{')

        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if(f'WHILE_END{idx}')
        self.compile_statements()
        self.vm_writer.write_goto(f'WHILE_EXP{idx}')
        self.vm_writer.write_label(f'WHILE_END{idx}')
        self.expect('}')

    def compile_do_statement(self):
        self.expect('do')
        self.compile_subroutine_call()
        self.vm_writer.write_pop('temp', 0)
        self.expect(';')

    def compile_return_statement(self):
        self.expect('return')

        next_token = self.tokenizer.lookahead()
        if next_token.token != ';':
            self.compile_expression()
        else:
            self.vm_writer.write_push('constant', 0)

        self.vm_writer.write_return()
        self.expect(';')

    def compile_subroutine_call(self):
        identifier = self.validate_identifier()
        n_args = 0
        next_token = self.tokenizer.lookahead()
        if next_token.token == '.':
            self.expect('.')
            function_name = self.validate_identifier()
            try:
                var = self.symbol_table.lookup(identifier)
                self.vm_writer.write_push(get_segment(var.kind), var.idx)
                function_name = f'{var.var_type}.{function_name}'
                n_args += 1
            except KeyError:
                function_name = f'{identifier}.{function_name}'
        else:
            function_name = f'{self.class_name}.{identifier}'
            n_args += 1
            self.vm_writer.write_push('pointer', 0)

        self.expect('(')
        n_args += self.compile_expression_list()
        self.expect(')')

        self.vm_writer.write_call(function_name, n_args)

    def compile_expression_list(self):
        n_expressions = 0
        next_token = self.tokenizer.lookahead()
        while next_token.token != ')':
            n_expressions += 1
            if next_token.token == ',':
                self.expect(',')
            self.compile_expression()
            next_token = self.tokenizer.lookahead()
        return n_expressions

    def compile_expression(self):
        self.compile_term()

        next_token = self.tokenizer.lookahead()
        while next_token.token in list('+-*/&|<>='):
            op = self.expect(next_token.token)
            self.compile_term()

            if op == '*':
                self.vm_writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.vm_writer.write_call('Math.divide', 2)
            else:
                op = ARITHMETIC_LOOKUP[op]
                self.vm_writer.write_arithmetic(op)

            next_token = self.tokenizer.lookahead()

    def compile_term(self):
        next_token = self.tokenizer.lookahead()
        ttype = next_token.token_type
        token = next_token.token
        if ttype == Tokens.INTEGER_CONST:
            self.expect(token)
            self.vm_writer.write_push('constant', token)
        elif ttype == Tokens.STRING_CONST:
            self.expect(token)
            self.compile_string(token)
        elif token in KEYWORD_CONSTS:
            keyword = self.expect(token)
            self.compile_keyword(keyword)
        elif token == '(':
            self.expect('(')
            self.compile_expression()
            self.expect(')')
        elif token in UNARY_OPS:
            op = self.expect(token)
            op = UNARY_OP_LOOKUP[op]
            self.compile_term()
            self.vm_writer.write_arithmetic(op)
        else:
            next_next_token = self.tokenizer.lookahead(2)
            if next_next_token.token in ['(', '.']:
                self.compile_subroutine_call()
            elif next_next_token.token == '[':
                var_name = self.validate_identifier()
                var = self.symbol_table.lookup(var_name)
                self.expect('[')
                self.compile_expression()
                self.expect(']')
                self.vm_writer.write_push(get_segment(var.kind), var.idx)
                self.vm_writer.write_arithmetic('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)
            else:
                var_name = self.validate_identifier()
                var = self.symbol_table.lookup(var_name)
                self.vm_writer.write_push(get_segment(var.kind), var.idx)

    def compile_string(self, string):
        self.vm_writer.write_push('constant', len(string))
        self.vm_writer.write_call('String.new', 1)

        for c in string:
            self.vm_writer.write_push('constant', ord(c))
            self.vm_writer.write_call('String.appendChar', 2)

    def compile_keyword(self, keyword):
        if keyword == 'this':
            self.vm_writer.write_push('pointer', 0)
        else:
            self.vm_writer.write_push('constant', 0)
            if keyword == 'true':
                self.vm_writer.write_arithmetic('not')
