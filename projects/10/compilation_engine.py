from .tokenizer import Tokenizer
from .util import Tokens


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

    def compile(self):
        self.compile_class()

    def compile_class(self):
        '''
        class -> 'class' className '{' class_var_dec* subroutine_dec* '}'
        '''
        # 'class'
        self.tokenizer.advance()
        self.stack.append(self.tokenizer.keyword)
        self.write_badxml_open()
        self.write_badxml()

        # className
        self.tokenizer.advance()
        assert self.tokenizer.identifier == self.f_name
        self.write_badxml()

        # '{'
        self.tokenizer.advance()
        self.write_badxml()

        next_token = self.tokenizer.lookahead()
        # class_var_dec*
        while next_token.token in ['field', 'static']:
            self.compile_class_var_dec()
            next_token = self.tokenizer.lookahead()

        # subroutine_dec*
        while next_token.token in ['constructor', 'function', 'method']:
            self.compile_subroutine()
            next_token = self.tokenizer.lookahead()

        # '}'
        self.tokenizer.advance()
        self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

        assert not self.tokenizer.has_more_tokens()
        assert len(self.stack) == 0

    def compile_class_var_dec(self):
        '''
        class_var_dec -> ('static' | 'field') type var_name (',' var_name)* ';'
        '''
        self.stack.append('classVarDec')
        self.write_badxml_open()

        # ('static' | 'field')
        self.tokenizer.advance()
        self.write_badxml()

        # type
        self.tokenizer.advance()
        self.write_badxml()

        # var_name
        self.tokenizer.advance()
        self.write_badxml()

        self.tokenizer.advance()
        # (',' var_name)*
        while self.tokenizer.symbol == ',':
            self.write_badxml()
            # var_name
            self.tokenizer.advance()
            self.write_badxml()
            # ','
            self.tokenizer.advance()

        # ';'
        self.write_badxml()
        # end of class var dec
        self.write_badxml_close()
        self.stack.pop()

    def compile_subroutine(self):
        '''
        subroutine_dec -> ('constructor' | 'function' | 'method') ('void' | type)
                          name '(' var_list ')' subroutine_body
        '''
        self.stack.append('subroutineDec')
        self.write_badxml_open()

        # ('constructor' | 'function' | 'method')
        self.tokenizer.advance()
        self.write_badxml()

        # ('void' | type)
        self.tokenizer.advance()
        self.write_badxml()

        # name
        self.tokenizer.advance()
        self.write_badxml()

        # '('
        self.tokenizer.advance()
        self.write_badxml()

        self.compile_parameter_list()

        # ')'
        self.tokenizer.advance()
        self.write_badxml()

        self.compile_subroutine_body()

        self.write_badxml_close()
        self.stack.pop()

    def compile_parameter_list(self):
        '''
        parameter_list -> ((type name) (',' type name)*)
        '''
        self.stack.append("parameterList")
        self.write_badxml_open()

        next_token = self.tokenizer.lookahead()
        while next_token.token != ')':
            if next_token.token == ',':
                self.tokenizer.advance()
                self.write_badxml()
            # type
            self.tokenizer.advance()
            self.write_badxml()

            # name
            self.tokenizer.advance()
            self.write_badxml()

            next_token = self.tokenizer.lookahead()

        self.write_badxml_close()
        self.stack.pop()

    def compile_subroutine_body(self):
        '''
        subroutine_body -> '{' var_dec* statements '}'
        '''

        self.stack.append('subroutineBody')
        self.write_badxml_open()

        # '{'
        self.tokenizer.advance()
        self.write_badxml()

        next_token = self.tokenizer.lookahead()
        # var_dec*
        while next_token.token == 'var':
            self.compile_var_dec()
            next_token = self.tokenizer.lookahead()

        # statements
        self.compile_statements()

        # '}'
        self.tokenizer.advance()
        self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

    def compile_var_dec(self):
        '''
        var_dec -> 'var' type name (',' name)* ';'
        '''
        self.stack.append('varDec')
        self.write_badxml_open()

        # 'var'
        self.tokenizer.advance()
        self.write_badxml()

        # type
        self.tokenizer.advance()
        self.write_badxml()

        # name
        self.tokenizer.advance()
        self.write_badxml()

        next_token = self.tokenizer.lookahead()
        while next_token.token == ',':
            # ','
            self.tokenizer.advance()
            self.write_badxml()
            # name
            self.tokenizer.advance()
            self.write_badxml()
            next_token = self.tokenizer.lookahead()

        # ';'
        self.tokenizer.advance()
        self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

    def compile_statements(self):
        '''
        statements -> statement*
        '''
        self.stack.append('statements')
        self.write_badxml_open()

        next_token = self.tokenizer.lookahead()
        while next_token.token != '}':
            self.compile_statement()
            next_token = self.tokenizer.lookahead()

        self.write_badxml_close()
        self.stack.pop()

    def compile_statement(self):
        '''
        statement -> let_statement | if_statement | while_statement |
                     do_statement | return_statement
        '''
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
        '''
        let_statement -> 'let' name ('[' expression ']')? '=' expression ';'
        '''
        self.stack.append('letStatement')
        self.write_badxml_open()

        # 'let'
        self.tokenizer.advance()
        self.write_badxml()

        # name
        self.tokenizer.advance()
        self.write_badxml()

        # ('[' expression ']')?
        next_token = self.tokenizer.lookahead()
        if next_token.token == '[':
            # '['
            self.tokenizer.advance()
            self.write_badxml()
            # expression
            self.compile_expression()
            # ']'
            self.tokenizer.advance()
            self.write_badxml()
            next_token = self.tokenizer.lookahead()

        # '='
        self.tokenizer.advance()
        self.write_badxml()

        # expression
        self.compile_expression()

        # ';'
        self.tokenizer.advance()
        self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

    def compile_if_statement(self):
        '''
        if_statement -> 'if' '(' expression ')' '{' statements '}'
                        ('else' '{' statments '}')?
        '''
        self.stack.append('ifStatement')
        self.write_badxml_open()

        # 'if'
        self.tokenizer.advance()
        self.write_badxml()

        # '('
        self.tokenizer.advance()
        self.write_badxml()

        # expression
        self.compile_expression()

        # ')'
        self.tokenizer.advance()
        self.write_badxml()

        # '{'
        self.tokenizer.advance()
        self.write_badxml()

        # statements
        self.compile_statements()

        # '}'
        self.tokenizer.advance()
        self.write_badxml()

        next_token = self.tokenizer.lookahead()
        if next_token.token == 'else':
            # 'else'
            self.tokenizer.advance()
            self.write_badxml()
            # '{'
            self.tokenizer.advance()
            self.write_badxml()
            # statements
            self.compile_statements()
            # '}'
            self.tokenizer.advance()
            self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

    def compile_while_statement(self):
        '''
        while_statement -> 'while' '(' expression ')' '{' statements '}'
        '''
        self.stack.append('whileStatement')
        self.write_badxml_open()

        # 'while'
        self.tokenizer.advance()
        self.write_badxml()

        # '('
        self.tokenizer.advance()
        self.write_badxml()

        # expression
        self.compile_expression()

        # ')'
        self.tokenizer.advance()
        self.write_badxml()

        # '{'
        self.tokenizer.advance()
        self.write_badxml()

        # statements
        self.compile_statements()

        # '}'
        self.tokenizer.advance()
        self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

    def compile_do_statement(self):
        '''
        do_statement -> 'do' subroutine_call ';'
        '''
        self.stack.append('doStatement')
        self.write_badxml_open()

        # 'do'
        self.tokenizer.advance()
        self.write_badxml()

        # subroutine_call
        self.compile_subroutine_call()

        # ';'
        self.tokenizer.advance()
        self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

    def compile_return_statement(self):
        '''
        return_statement -> 'return' expression? ';'
        '''
        self.stack.append('returnStatement')
        self.write_badxml_open()

        # 'return'
        self.tokenizer.advance()
        self.write_badxml()

        next_token = self.tokenizer.lookahead()
        if next_token.token != ';':
            self.compile_expression()
            next_token = self.tokenizer.lookahead()

        # ';'
        self.tokenizer.advance()
        self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

    def compile_subroutine_call(self):
        '''
        subroutine_call -> subroutine_name '(' expression_list ')' |
                           (class_name | var_name) '.' subroutine_name '(' expression_list ')'
        '''

        # subroutine_name | (class_name | var_name)
        self.tokenizer.advance()
        self.write_badxml()

        next_token = self.tokenizer.lookahead()
        if next_token.token == '.':
            # '.'
            self.tokenizer.advance()
            self.write_badxml()
            # subroutine_name
            self.tokenizer.advance()
            self.write_badxml()
            next_token = self.tokenizer.lookahead()

        # '('
        self.tokenizer.advance()
        self.write_badxml()

        # expression_list
        self.compile_expression_list()

        # ')'
        self.tokenizer.advance()
        self.write_badxml()

    def compile_expression_list(self):
        '''
        expression_list -> (expression (',' expression)*)?
        '''
        self.stack.append('expressionList')
        self.write_badxml_open()

        next_token = self.tokenizer.lookahead()
        while next_token.token != ')':
            if next_token.token == ',':
                self.tokenizer.advance()
                self.write_badxml()
            self.compile_expression()
            next_token = self.tokenizer.lookahead()

        self.write_badxml_close()
        self.stack.pop()

    def compile_expression(self):
        '''
        expression -> term (op term)*
        '''
        self.stack.append('expression')
        self.write_badxml_open()

        # term
        self.compile_term()

        next_token = self.tokenizer.lookahead()
        while next_token.token in list('+-*/&|<>='):
            # op
            self.tokenizer.advance()
            self.write_badxml()
            # term
            self.compile_term()
            next_token = self.tokenizer.lookahead()

        self.write_badxml_close()
        self.stack.pop()

    def compile_term(self):
        '''
        term -> integer_const | string_const | keyword_const | var_name |
                var_name '[' expression ']' | subroutine_call | '(' expression ')' |
                unary_op term
        '''
        self.stack.append('term')
        self.write_badxml_open()

        const_types = [Tokens.INTEGER_CONST, Tokens.STRING_CONST]
        const_keywords = ['true', 'false', 'null', 'this']
        next_token = self.tokenizer.lookahead()
        ttype = next_token.token_type
        token = next_token.token
        # integer_const | string_const | keyword_const
        if ttype in const_types or token in const_keywords:
            # const
            self.tokenizer.advance()
            self.write_badxml()
        # '(' expression ')'
        elif next_token.token == '(':
            # '('
            self.tokenizer.advance()
            self.write_badxml()
            # expression
            self.compile_expression()
            # ')'
            self.tokenizer.advance()
            self.write_badxml()
        # unary_op term
        elif next_token.token in ['-', '~']:
            # unary_op
            self.tokenizer.advance()
            self.write_badxml()
            # term
            self.compile_term()
        else:
            next_next_token = self.tokenizer.lookahead(2)
            if next_next_token.token in ['(', '.']:
                # subroutine_call
                self.compile_subroutine_call()
            elif next_next_token.token == '[':
                # var_name
                self.tokenizer.advance()
                self.write_badxml()
                # '['
                self.tokenizer.advance()
                self.write_badxml()
                # expression
                self.compile_expression()
                # ']'
                self.tokenizer.advance()
                self.write_badxml()
            else:
                # var_name
                self.tokenizer.advance()
                self.write_badxml()

        self.write_badxml_close()
        self.stack.pop()

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
