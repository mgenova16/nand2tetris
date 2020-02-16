from .instruction import Instruction
from .helper import dec_to_bin
from .helper import sym_table


class Assembler():

    def __init__(self, filename):
        self.asm_file = filename
        self.hack_file = filename.replace('.asm', '.py.hack')
        self.rom_addr = 0
        self.next_ram_addr = 16
        self.sym_table = sym_table()
        self.instructions = []
        self.machine_instructions = []

    def assemble(self):
        self._build_sym_table()
        self._translate()
        self._write()

    def _build_sym_table(self):
        with open(self.asm_file, 'r') as f:
            for line in f:
                instruction = Instruction(line)
                instruction.parse()
                if instruction.is_comment:
                    continue
                if instruction.is_L_command:
                    if instruction.symbol not in self.sym_table:
                        self.sym_table[instruction.symbol] = self.rom_addr
                    else:
                        err = 'Already defined: {}'.format(instruction.symbol)
                        raise Exception(err)
                else:
                    self.rom_addr += 1
                    self.instructions.append(instruction)

    def _translate(self):
        for instruction in self.instructions:
            if instruction.is_C_command:
                start_bits = '111'
                c_bits = instruction.comp_bin
                d_bits = instruction.dest_bin
                j_bits = instruction.jump_bin
                machine_instruction = start_bits + c_bits + d_bits + j_bits
                self.machine_instructions.append(machine_instruction)
            elif instruction.is_A_command:
                if instruction.symbol_bin is not None:
                    self.machine_instructions.append(instruction.symbol_bin)
                else:
                    if instruction.symbol not in self.sym_table:
                        self.sym_table[instruction.symbol] = self.next_ram_addr
                        self.next_ram_addr += 1
                    val = self.sym_table[instruction.symbol]
                    bin_val = dec_to_bin(val, '#018b')
                    self.machine_instructions.append(bin_val)

    def _write(self):
        with open(self.hack_file, 'w') as f:
            for mi in self.machine_instructions:
                f.write(mi + '\n')
