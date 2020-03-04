ADDR_SP = '@SP'
ADDR_LCL = '@LCL'
ADDR_ARG = '@ARG'
ADDR_THIS = '@THIS'
ADDR_THAT = '@THAT'
FRAME_ADDRS = {
    'local': ADDR_LCL,
    'argument': ADDR_ARG,
    'this': ADDR_THIS,
    'that': ADDR_THAT,
}

CMD_ADD = 'add'
CMD_SUB = 'sub'
CMD_NEG = 'neg'
CMD_AND = 'and'
CMD_OR = 'or'
CMD_NOT = 'not'
CMDS_MATH = [CMD_ADD, CMD_SUB, CMD_NEG, CMD_AND, CMD_OR, CMD_NOT]

CMD_EQ = 'eq'
CMD_LT = 'lt'
CMD_GT = 'gt'
CMDS_COMP = [CMD_EQ, CMD_LT, CMD_GT]

CMD_PUSH = 'push'
CMD_POP = 'pop'

CMD_LABEL = 'label'
CMD_GOTO = 'goto'
CMD_IF_GOTO = 'if-goto'

CMD_FUNCTION = 'function'
CMD_CALL = 'call'
CMD_RETURN = 'return'
