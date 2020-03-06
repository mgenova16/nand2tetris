A_SP = '@SP'
A_LCL = '@LCL'
A_ARG = '@ARG'
A_THIS = '@THIS'
A_THAT = '@THAT'
FRAME_ADDRS = {
    'local': A_LCL,
    'argument': A_ARG,
    'this': A_THIS,
    'that': A_THAT,
}

CMD_ADD = 'add'
CMD_SUB = 'sub'
CMD_NEG = 'neg'
CMD_AND = 'and'
CMD_OR = 'or'
CMD_NOT = 'not'
MATH_COMMANDS = [CMD_ADD, CMD_SUB, CMD_NEG, CMD_AND, CMD_OR, CMD_NOT]

CMD_EQ = 'eq'
CMD_LT = 'lt'
CMD_GT = 'gt'
COMPARISON_COMMANDS = [CMD_EQ, CMD_LT, CMD_GT]

CMD_PUSH = 'push'
CMD_POP = 'pop'

CMD_LABEL = 'label'
CMD_GOTO = 'goto'
CMD_IF_GOTO = 'if-goto'
PROGRAM_FLOW_COMMANDS = [CMD_LABEL, CMD_GOTO, CMD_IF_GOTO]

CMD_FUNCTION = 'function'
CMD_CALL = 'call'
CMD_RETURN = 'return'
