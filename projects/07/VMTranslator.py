#!/usr/bin/env python3

import sys
from pathlib import Path


def main():
    in_files, out_file = get_files()
    with open(out_file, 'w') as f_out:
        for f in in_files:
            with open(f, 'r') as f_in:
                for line in f_in:
                    asm = translate(line, f.stem)
                    f_out.write(asm)


def get_files():
    p = Path(sys.argv[1])
    vm_files = list(p.glob('*.vm')) if p.is_dir() else [p]
    base_dir = p if p.is_dir() else p.parent
    asm_file = base_dir / vm_files[0].name.replace('vm', 'asm')
    return vm_files, asm_file


def translate(line, f):
    command, *args = line.split('//')[0].strip().split(' ')
    if len(command) == 0:
        return ''
    cmds = []
    if command in math_ops:
        cmds += translate_math(command)
    elif command in comp_ops:
        cmds += translate_comp(command)
    elif command in mem_ops:
        cmds += translate_mem(f, command, *args)
    return '\n'.join(cmds) + '\n'


def translate_math(command):
    cmds = []
    n = n_args(command)
    cmds += args_from_stack(n)
    cmds += [math_ops[command]['asm_op']]
    cmds += inc_sp()
    return cmds


def translate_comp(command):
    cmds = []
    comp_count = next(comp_counter)
    cmds += args_from_stack(2)
    cmds += ['D=M-D']
    cmds += ['@COMP_JUMP.{}'.format(comp_count)]
    cmds += [comp_ops[command]]
    cmds += ['@SP']
    cmds += ['A=M']
    cmds += ['M=0']
    cmds += ['@INC_SP_JUMP.{}'.format(comp_count)]
    cmds += ['0;JMP']
    cmds += ['(COMP_JUMP.{})'.format(comp_count)]
    cmds += ['@SP']
    cmds += ['A=M']
    cmds += ['M=-1']
    cmds += ['(INC_SP_JUMP.{})'.format(comp_count)]
    cmds += inc_sp()
    return cmds


def translate_mem(f, command, segment, index):
    cmds = []
    cmds += set_a_to_address(f, segment, index)
    if command == 'push':
        if segment == 'constant':
            cmds += ['D=A']
        else:
            cmds += ['D=M']
        cmds += ['@SP']
        cmds += ['A=M']
        cmds += ['M=D']
        cmds += inc_sp()
    else:
        cmds += ['D=A']
        cmds += ['@R13']
        cmds += ['M=D']
        cmds += dec_sp()
        cmds += ['A=M']
        cmds += ['D=M']
        cmds += ['@R13']
        cmds += ['A=M']
        cmds += ['M=D']
    return cmds


def args_from_stack(n):
    cmds = []
    cmds += dec_sp()
    cmds += ['A=M']
    if n == 2:
        cmds += ['D=M']
        cmds += dec_sp()
        cmds += ['A=M']
    return cmds



def comp_incrementer():
    i = 0
    while True:
        yield i
        i += 1


def dec_sp():
    return ['@SP', 'M=M-1']


def inc_sp():
    return ['@SP', 'M=M+1']


def n_args(command):
    return math_ops[command]['n_args']



def set_a_to_address(f, segment, index):
    lookup = segment_lookups[segment]
    return lookup(index, f)


math_ops = {
    'add': {'asm_op': 'M=M+D', 'n_args': 2},
    'sub': {'asm_op': 'M=M-D', 'n_args': 2},
    'neg': {'asm_op':  'M=-M', 'n_args': 1},
    'and': {'asm_op': 'M=M&D', 'n_args': 2},
    'or':  {'asm_op': 'M=M|D', 'n_args': 2},
    'not': {'asm_op':  'M=!M', 'n_args': 1},
}

comp_ops = {'eq': 'D;JEQ', 'lt': 'D;JLT', 'gt': 'D;JGT'}

mem_ops = ['push', 'pop']

segment_lookups = {
    'local':    lambda i, f: '@LCL D=M @{} A=D+A'.format(i).split(),
    'argument': lambda i, f: '@ARG D=M @{} A=D+A'.format(i).split(),
    'this':     lambda i, f: '@THIS D=M @{} A=D+A'.format(i).split(),
    'that':     lambda i, f: '@THAT D=M @{} A=D+A'.format(i).split(),
    'pointer':  lambda i, f: '@R{}'.format(3 + int(i)).split(),
    'temp':     lambda i, f: '@R{}'.format(5 + int(i)).split(),
    'static':   lambda i, f: '@{}.{}'.format(f, i).split(),
    'constant': lambda i, f: '@{}'.format(i).split(),
}

comp_counter = comp_incrementer()

if __name__ == '__main__':
    main()
