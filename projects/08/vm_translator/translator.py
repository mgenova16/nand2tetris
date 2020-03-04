from .parser import Parser


class Translator:

    def __init__(self, p):
        self.vm_files = list(p.glob('*.vm')) if p.is_dir() else [p]
        base_dir = p if p.is_dir() else p.parent
        self.asm_file = base_dir / (base_dir.name + ".asm")

    def translate_all(self):
        with open(self.asm_file, 'w') as f:
            for vm_file in self.vm_files:
                print(f'{vm_file}')
                parser = Parser(vm_file, f)
                parser.parse()
