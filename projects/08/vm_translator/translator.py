from .command import CallCommand
from .parser import Parser


class Translator:

    def __init__(self, p):
        base_dir = p if p.is_dir() else p.parent
        self.asm_file = base_dir / (base_dir.name + '.asm')
        self.vm_files = list(p.glob('*.vm')) if p.is_dir else [p]

    def translate_all(self):
        with open(self.asm_file, 'w') as f:
            if 'Sys.vm' in [f.name for f in self.vm_files]:
                self.write_bootstrap_code(f)
            for vm_file in self.vm_files:
                parser = Parser(vm_file, f)
                parser.parse()

    def write_bootstrap_code(self, out_file):
        out_file.write('@256\n')
        out_file.write('D=A\n')
        out_file.write('@SP\n')
        out_file.write('M=D\n')
        cmd = CallCommand('call', '', 'Sys.init', 0)
        cmd.translate()
        out_file.write('\n'.join(cmd.assembly) + '\n')
