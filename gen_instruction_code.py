def gen_for_PSM(lex, opt, instruction_list):
    """
    Генерує інструкції для постфікс-машини

    Parameters:
    - lex: лексема (символ, ідентифікатор, значення)
    - opt: тип операції
    - instruction_list: список для додавання інструкцій
    """

    if opt == 'l-val':
        instr = (lex, 'l-val')
    elif opt == 'r-val':
        instr = (lex, 'r-val')
    elif lex == '=':
        instr = ('=', 'assign_op')
    elif opt == 'label':
        instr = (lex, 'label')
    elif opt == 'colon':
        instr = (':', 'colon')
    elif opt in ['int', 'float', 'bool', 'string']:
        instr = (lex, opt)
    elif lex == '+':
        instr = ('+', 'math_op')
    elif lex == '-':
        instr = ('-', 'math_op')
    elif lex == '*':
        instr = ('*', 'math_op')
    elif lex == '/':
        instr = ('/', 'math_op')
    elif lex == '%':
        instr = ('%', 'math_op')
    elif lex == 'neg':
        instr = ('NEG', 'math_op')
    elif lex == '**':
        instr = ('^', 'pow_op')
    elif lex == '>':
        instr = ('>', 'rel_op')
    elif lex == '<':
        instr = ('<', 'rel_op')
    elif lex == '>=':
        instr = ('>=', 'rel_op')
    elif lex == '<=':
        instr = ('<=', 'rel_op')
    elif lex == '==':
        instr = ('==', 'rel_op')
    elif lex == '!=':
        instr = ('!=', 'rel_op')
    elif lex == 'print':
        instr = ('OUT', 'out_op')
    elif lex == 'readLine':
        instr = ('INP', 'inp_op')
    elif lex == 'i2f':
        instr = ('i2f', 'conv')
    elif lex == 'f2i':
        instr = ('f2i', 'conv')
    elif lex == 'i2s':
        instr = ('i2s', 'conv')
    elif lex == 's2i':
        instr = ('s2i', 'conv')
    elif lex == 'f2s':
        instr = ('f2s', 'conv')
    elif lex == 's2f':
        instr = ('s2f', 'conv')
    elif lex == 'b2i':
        instr = ('b2i', 'conv')
    elif lex == 'i2b':
        instr = ('i2b', 'conv')
    elif lex == '!':
        instr = ('NOT', 'bool_op')
    elif lex == '&&':
        instr = ('AND', 'bool_op')
    elif lex == '||':
        instr = ('OR', 'bool_op')
    elif lex == 'jf' or opt == 'jf':
        instr = ('JF', 'jf')
    elif lex == 'jump' or opt == 'jump':
        instr = ('JUMP', 'jump')
    elif lex == ':':
        instr = (':', 'colon')
    elif opt == 'call':
        instr = (lex, 'CALL')
    elif lex == 'return':
        instr = ('RET', '')
    elif opt == 'concat':
        instr = ('CAT', 'cat_op')
    elif lex == 'pop':
        instr = ('POP', 'stack_op')
    elif lex == 'dup':
        instr = ('DUP', 'stack_op')
    elif lex == 'swap':
        instr = ('SWAP', 'stack_op')
    elif lex == 'nop':
        instr = ('NOP', 'stack_op')
    else:
        print(f"Неочікуване значення lex або opt: lex = {lex}; opt = {opt}")
        exit(1)

    instruction_list.append(instr)
    return True