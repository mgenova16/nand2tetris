from .tokenizer import Tokenizer


class CompilationEngine:

    def __init__(self, in_file, out_file):
        self.in_file = open(in_file, 'r')
        self.out_file = open(out_file, 'w')
        self.tokenizer = Tokenizer(self.in_file)

    def __del__(self):
        self.in_file.close()
        self.out_file.close()

    def compile(self):
        self.out_file.write('<tokens>\n')
        while self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            self.out_file.write(f'{self.tokenizer}\n')
        self.out_file.write('</tokens>\n')
