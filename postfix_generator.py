import os
from prettytable import PrettyTable

import lex_qirim
import syntax_qirim

postfixCode = []
tableOfLabel = {}
OUTPUT_DIR = "output"


def extract_variables_from_postfix():
    """Витягує всі змінні з постфікс-коду та визначає їх типи"""
    variables = {}
    
    for i, (lex, tok) in enumerate(postfixCode):
        if tok == 'l-val':
            var_name = lex
            
            if i + 1 < len(postfixCode):
                next_lex, next_tok = postfixCode[i + 1]
                
                if next_tok == 'int':
                    variables[var_name] = 'int'
                elif next_tok == 'float':
                    variables[var_name] = 'float'
                elif next_tok == 'string':
                    variables[var_name] = 'string'
                elif next_tok == 'bool':
                    variables[var_name] = 'bool'
                elif next_tok == 'r-val':
                    if next_lex in variables:
                        variables[var_name] = variables[next_lex]
                    else:
                        variables[var_name] = 'int'
                elif next_tok == 'inp_op':
                    variables[var_name] = 'string'
                elif next_tok == 'CALL':
                    variables[var_name] = 'int'
                else:
                    if var_name not in variables:
                        variables[var_name] = 'int'
    
    return variables


class PostfixGenerator:
    def __init__(self):
        self.postfix = []
        self.labels = {}
        self.label_counter = 0
        
    def generate_label(self):
        self.label_counter += 1
        label_name = f"m{self.label_counter}"
        self.labels[label_name] = 'val_undef'
        return label_name
    
    def set_label(self, label_name):
        self.labels[label_name] = len(self.postfix)
    
    def add(self, lexeme, token):
        self.postfix.append((lexeme, token))


def save_postfix_to_file(filename="test"):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.postfix")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(".target: Postfix Machine\n")
        f.write(".version: 0.2\n")
        
        f.write(".vars(\n")
        all_vars = {}
        
        if hasattr(syntax_qirim, 'tableOfVar') and syntax_qirim.tableOfVar:
            all_vars.update(syntax_qirim.tableOfVar)
        
        if hasattr(syntax_qirim, 'tableOfVarByFunction') and syntax_qirim.tableOfVarByFunction:
            for func_vars in syntax_qirim.tableOfVarByFunction.values():
                if func_vars:
                    all_vars.update(func_vars)
        
        if not all_vars:
            print("\n⚠️ ПОПЕРЕДЖЕННЯ: tableOfVar порожній, збираємо змінні з постфікс-коду...")
            all_vars = extract_variables_from_postfix()
        
        for var_name, var_info in all_vars.items():
            if isinstance(var_info, dict) and 'type' in var_info:
                var_type = var_info['type'].lower()
            elif isinstance(var_info, str):
                var_type = var_info.lower()
            else:
                var_type = str(var_info).lower()
            
            if var_type == 'real':
                var_type = 'float'
            elif var_type == 'boolean':
                var_type = 'bool'
            
            f.write(f"{var_name} {var_type}\n")
        f.write(")\n")
        
        f.write(".funcs(\n")
        if hasattr(syntax_qirim, 'tableOfFunc') and syntax_qirim.tableOfFunc:
            for func_name, func_info in syntax_qirim.tableOfFunc.items():
                if func_name == 'main':
                    continue
                if isinstance(func_info, dict):
                    ret_type = func_info.get('type', 'void').lower()
                    params = func_info.get('params', [])
                    n_params = len(params) if params else 0
                else:
                    ret_type = 'void'
                    n_params = 0
                
                if ret_type == 'real':
                    ret_type = 'float'
                elif ret_type == 'boolean':
                    ret_type = 'bool'
                
                f.write(f"{func_name} {ret_type} {n_params}\n")
        f.write(")\n")
        
        f.write(".globVarList(\n")
        f.write(")\n")
        
        f.write(".labels(\n")
        for label_name, label_value in tableOfLabel.items():
            if label_value != 'val_undef':
                f.write(f"{label_name} {label_value}\n")
        f.write(")\n")
        
        f.write(".constants(\n")
        for const in lex_qirim.tableOfConst.keys():
            f.write(f"{const}\n")
        f.write(")\n")
        
        f.write(".code(\n")
        for lex, tok in postfixCode:
            f.write(f"{lex} {tok}\n")
        f.write(")\n")
    
    print(f"\nPostfix-код збережено у файл: {filepath}")
    return filepath


def print_postfix_code():
    print("\n" + "="*60)
    print("ПОСТФІКС-КОД (ПОЛІЗ)")
    print("="*60)
    
    if not postfixCode:
        print("(порожній)")
    else:
        table = PrettyTable()
        table.field_names = ["№", "Лексема", "Токен"]
        
        for i, (lex, tok) in enumerate(postfixCode):
            table.add_row([i, lex, tok])
        
        print(table)
    
    print("\nТаблиця міток:")
    label_table = PrettyTable()
    label_table.field_names = ["Мітка", "Позиція"]
    for label, pos in sorted(tableOfLabel.items(), key=lambda x: x[1] if x[1] != 'val_undef' else 999999):
        label_table.add_row([label, pos])
    print(label_table)


def convert_token_for_psm(token, lexeme):
    token_map = {
        'logical_op': 'bool_op',
        'add_op': 'math_op',
        'mult_op': 'math_op',
        'exp_op': 'pow_op',
        'rel_op': 'rel_op',
        'assign_op': 'assign_op',
        'brackets_op': 'brackets_op',
        'punct': 'punct',
        'int_const': 'int',
        'real_const': 'float',
        'string_const': 'string',
        'bool_const': 'bool',
        'identifier': 'identifier',
        'keyword': 'keyword',
        'colon': 'colon',
        'label': 'label',
        'jf': 'jf',
        'jump': 'jump',
        'out_op': 'out_op',
        'l-val': 'l-val',
        'r-val': 'r-val',
        'CALL': 'CALL',
        'RET': 'RET'
    }
    
    if token == 'logical_op':
        if lexeme == '&&':
            return 'AND', 'bool_op'
        elif lexeme == '||':
            return 'OR', 'bool_op'
        elif lexeme == '!':
            return 'NOT', 'bool_op'
    
    if token == 'exp_op' and lexeme == '**':
        return '^', 'pow_op'
    
    if token in ('int_const', 'real_const', 'string_const', 'bool_const', 'l-val', 'r-val'):
        return lexeme, token_map.get(token, token)
    
    return lexeme, token_map.get(token, token)


def generate_simple_postfix():
    global postfixCode, tableOfLabel
    
    postfixCode = []
    tableOfLabel = {}
    
    generator = PostfixGenerator()
    tableOfSymb = lex_qirim.tableOfSymb
    
    i = 1
    inside_main = False
    brace_depth = 0
    max_iterations = len(tableOfSymb) * 2
    iterations = 0
    
    while i <= len(tableOfSymb):
        iterations += 1
        if iterations > max_iterations:
            print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Можливий нескінченний цикл на позиції {i}")
            print(f"Поточний токен: {tableOfSymb[i] if i <= len(tableOfSymb) else 'EOF'}")
            break
        
        numLine, lex, tok, idx = tableOfSymb[i]
        
        if lex == 'fun' and tok == 'keyword':
            if i + 1 <= len(tableOfSymb):
                _, next_lex, _, _ = tableOfSymb[i + 1]
                if next_lex == 'main':
                    inside_main = True
                    i += 1
                    continue
            i += 1
            continue
        
        if inside_main:
            if tok == 'brackets_op':
                if lex == '{':
                    brace_depth += 1
                    i += 1
                    continue
                elif lex == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        inside_main = False
                    i += 1
                    continue
        
        if not inside_main:
            i += 1
            continue
        
        old_i = i
        i = process_statement(i, tableOfSymb, generator)
        
        if i == old_i:
            print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Застряг на позиції {i}, токен: {tableOfSymb[i]}")
            i += 1
    
    postfixCode = generator.postfix
    tableOfLabel = generator.labels
    
    return postfixCode, tableOfLabel


def process_statement(i, table, gen):
    if i > len(table):
        return i
    
    _, lex, tok, _ = table[i]
    
    if lex == ';':
        return i + 1
    
    if tok == 'keyword' and lex in ('var', 'val'):
        return gen_variable_declaration(i, table, gen)
    
    if tok == 'identifier':
        if i + 1 <= len(table):
            _, next_lex, next_tok, _ = table[i + 1]
            
            if next_lex == '=' and next_tok == 'assign_op':
                return gen_assignment(i, table, gen)
            elif next_lex == '(' and next_tok == 'brackets_op':
                i = gen_func_call(i, table, gen)
                if hasattr(syntax_qirim, 'tableOfFunc') and lex in syntax_qirim.tableOfFunc:
                    func_info = syntax_qirim.tableOfFunc[lex]
                    if isinstance(func_info, dict):
                        ret_type = func_info.get('type', 'void')
                    else:
                        ret_type = 'void'
                    
                    if ret_type != 'void':
                        gen.add('POP', 'stack_op')
                
                if i <= len(table):
                    _, lex2, tok2, _ = table[i]
                    if lex2 == ';':
                        i += 1
                return i
    
    if tok == 'keyword':
        if lex == 'if':
            return gen_if(i, table, gen)
        elif lex == 'for':
            return gen_for(i, table, gen)
        elif lex == 'while':
            return gen_while(i, table, gen)
        elif lex == 'do':
            return gen_do_while(i, table, gen)
        elif lex == 'when':
            return gen_when(i, table, gen)
        elif lex == 'print':
            return gen_print(i, table, gen)
    
    return i + 1


def gen_variable_declaration(start, table, gen):
    i = start
    _, keyword, _, _ = table[i]
    i += 1
    
    _, var_name, _, _ = table[i]
    i += 1
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == ':':
            i += 1
            i += 1
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == '=' and tok == 'assign_op':
            i += 1
            
            if i <= len(table):
                _, next_lex, next_tok, _ = table[i]
                if next_lex == 'readLine' and next_tok == 'keyword':
                    gen.add(var_name, 'l-val')
                    gen.add('IN', 'inp_op')
                    gen.add(':=', 'assign_op')
                    i += 1
                    if i <= len(table):
                        _, lex2, _, _ = table[i]
                        if lex2 == '(':
                            i += 1
                        if i <= len(table):
                            _, lex3, _, _ = table[i]
                            if lex3 == ')':
                                i += 1
                else:
                    gen.add(var_name, 'l-val')
                    i = gen_expr(i, table, gen, until=[';'])
                    gen.add(':=', 'assign_op')
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == ';':
            i += 1
    
    return i


def gen_assignment(start, table, gen):
    i = start
    _, var_name, _, _ = table[i]
    
    gen.add(var_name, 'l-val')  # Используем l-val для присваивания
    i += 1
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == '=' and tok == 'assign_op':
            i += 1
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == 'readLine' and tok == 'keyword':
            gen.add('IN', 'inp_op')
            gen.add(':=', 'assign_op')
            i += 1
            if i <= len(table):
                _, lex2, _, _ = table[i]
                if lex2 == '(':
                    i += 1
                if i <= len(table):
                    _, lex3, _, _ = table[i]
                    if lex3 == ')':
                        i += 1
            return i
    
    old_i = i
    i = gen_expr(i, table, gen, until=[';'])
    if i > old_i:  # Если выражение было сгенерировано
        gen.add(':=', 'assign_op')
    
    return i


def gen_expr(start, table, gen, until=None):
    if until is None:
        until = [';', ')', ',', '{', '}']
    
    i = start
    op_stack = []
    expect_unary = True
    
    prec = {
        '||': 1, '&&': 2,
        '==': 3, '!=': 3,
        '<': 4, '<=': 4, '>': 4, '>=': 4,
        '+': 5, '-': 5,
        '*': 6, '/': 6, '%': 6,
        '**': 7,
        'UNARY': 8
    }
    
    while i <= len(table):
        _, lex, tok, _ = table[i]
        
        if lex in until:
            break
        
        if tok == 'keyword' and lex in ('if', 'for', 'while', 'do', 'when', 'print', 'var', 'val', 'else'):
            break
        
        if tok == 'keyword' and lex == 'if':
            i = gen_ternary_if(i, table, gen)
            expect_unary = False
            continue
        
        if expect_unary and tok == 'logical_op' and lex == '!':
            op_stack.append(('!', 'UNARY_NOT'))
            i += 1
            continue
        
        if expect_unary and tok == 'add_op' and lex in ('+', '-'):
            if lex == '-':
                op_stack.append(('-', 'UNARY_MINUS'))
            i += 1
            continue
            
        if tok == 'identifier':
            if i + 1 <= len(table):
                _, nl, nt, _ = table[i + 1]
                if nl == '(' and nt == 'brackets_op':
                    func_name = lex
                    i += 1
                    i += 1
                    
                    arg_count = 0
                    while i <= len(table):
                        _, lex2, tok2, _ = table[i]
                        
                        if lex2 == ')':
                            break
                            
                        if lex2 == ',':
                            i += 1
                            continue
                            
                        i = gen_expr(i, table, gen, until=[',', ')'])
                        arg_count += 1
                    
                    gen.add(func_name, 'CALL')
                    
                    if i <= len(table):
                        _, lex3, tok3, _ = table[i]
                        if lex3 == ')':
                            i += 1
                    
                    expect_unary = False
                    continue
                else:
                    _, next_lex2, next_tok2, _ = table[i + 1]
                    if next_lex2 == '=' and next_tok2 == 'assign_op':
                        gen.add(lex, 'l-val')  # Если следующий токен =, то это присваивание
                    else:
                        gen.add(lex, 'r-val')  # Иначе это использование значения
            i += 1
            expect_unary = False
            
        elif tok in ('int_const', 'real_const', 'bool_const'):
            typ_map = {'int_const': 'int', 'real_const': 'float', 'bool_const': 'bool'}
            gen.add(lex, typ_map[tok])
            i += 1
            expect_unary = False
        
        elif tok == 'string_const':
            gen.add(f'"{lex}"', 'string')
            i += 1
            expect_unary = False
            
        elif tok == 'brackets_op' and lex == '(':
            op_stack.append(('(', 'brackets_op'))
            i += 1
            expect_unary = True
            
        elif tok == 'brackets_op' and lex == ')':
            while op_stack and op_stack[-1][0] != '(':
                o, ot = op_stack.pop()
                if ot == 'UNARY_NOT':
                    gen.add('NOT', 'bool_op')
                elif ot == 'UNARY_MINUS':
                    gen.add('NEG', 'math_op')
                else:
                    o_conv, ot_conv = convert_token_for_psm(ot, o)
                    gen.add(o_conv, ot_conv)
            if op_stack:
                op_stack.pop()
            i += 1
            expect_unary = False
            
        elif tok in ('add_op', 'mult_op', 'exp_op', 'rel_op', 'logical_op'):
            while (op_stack and op_stack[-1][0] != '(' and
                   prec.get(op_stack[-1][1], 0) >= prec.get(lex, 0)):
                o, ot = op_stack.pop()
                if ot == 'UNARY_NOT':
                    gen.add('NOT', 'bool_op')
                elif ot == 'UNARY_MINUS':
                    gen.add('NEG', 'math_op')
                else:
                    o_conv, ot_conv = convert_token_for_psm(ot, o)
                    gen.add(o_conv, ot_conv)
            op_stack.append((lex, tok))
            i += 1
            expect_unary = True
        else:
            i += 1
    
    while op_stack:
        o, ot = op_stack.pop()
        if o != '(':
            if ot == 'UNARY_NOT':
                gen.add('NOT', 'bool_op')
            elif ot == 'UNARY_MINUS':
                gen.add('NEG', 'math_op')
            else:
                o_conv, ot_conv = convert_token_for_psm(ot, o)
                gen.add(o_conv, ot_conv)
    
    return i


def gen_ternary_if(start, table, gen):
    i = start + 1
    
    _, lex, tok, _ = table[i]
    if lex == '(':
        i += 1
    
    i = gen_expr(i, table, gen, until=[')'])
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == ')':
            i += 1
    
    m1 = gen.generate_label()
    m2 = gen.generate_label()
    
    gen.add(m1, 'label')
    gen.add('JF', 'jf')
    
    i = gen_expr(i, table, gen, until=['else'])
    
    gen.add(m2, 'label')
    gen.add('JMP', 'jump')
    
    gen.set_label(m1)
    gen.add(m1, 'label')
    gen.add(':', 'colon')
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == 'else':
            i += 1
            i = gen_expr(i, table, gen, until=[';', ')', ','])
    
    gen.set_label(m2)
    gen.add(m2, 'label')
    gen.add(':', 'colon')
    
    return i


def gen_func_call(start, table, gen):
    i = start
    _, func_name, _, _ = table[i]
    
    i += 1
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == '(':
            i += 1
    
    arg_count = 0
    while i <= len(table):
        _, lex, tok, _ = table[i]
        
        if lex == ')':
            break
            
        if lex == ',':
            i += 1
            continue
            
        i = gen_expr(i, table, gen, until=[',', ')'])
        arg_count += 1
    
    gen.add(func_name, 'CALL')
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == ')':
            i += 1
    
    return i


def gen_if(start, table, gen):
    i = start + 1
    
    _, lex, tok, _ = table[i]
    if lex == '(':
        i += 1
    
    i = gen_expr(i, table, gen, until=[')'])
    
    if i <= len(table):
        i += 1
    
    m1 = gen.generate_label()
    m2 = gen.generate_label()
    
    gen.add(m1, 'label')
    gen.add('JF', 'jf')
    
    i = gen_block(i, table, gen)
    
    gen.add(m2, 'label')
    gen.add('JMP', 'jump')
    
    gen.set_label(m1)
    gen.add(m1, 'label')
    gen.add(':', 'colon')
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == 'else':
            i += 1
            i = gen_block(i, table, gen)
    
    gen.set_label(m2)
    gen.add(m2, 'label')
    gen.add(':', 'colon')
    
    return i


def gen_for(start, table, gen):
    i = start + 1
    
    _, lex, tok, _ = table[i]
    if lex == '(':
        i += 1
    
    _, var_name, _, _ = table[i]
    i += 2
    
    gen.add(var_name, 'l-val')
    i = gen_expr(i, table, gen, until=['..', 'downTo', ')'])
    gen.add(':=', 'assign_op')
    
    m_start = gen.generate_label()
    m_end = gen.generate_label()
    
    gen.set_label(m_start)
    gen.add(m_start, 'label')
    gen.add(':', 'colon')
    
    gen.add(var_name, 'r-val')
    
    _, lex, tok, _ = table[i]
    if lex == '..':
        i += 1
        i = gen_expr(i, table, gen, until=['step', ')'])
        gen.add('<=', 'rel_op')
    elif lex == 'downTo':
        i += 1
        i = gen_expr(i, table, gen, until=['step', ')'])
        gen.add('>=', 'rel_op')
    
    step_val = '1'
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == 'step':
            i += 1
            _, step_val, _, _ = table[i]
            i += 1
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == ')':
            i += 1
    
    gen.add(m_end, 'label')
    gen.add('JF', 'jf')
    
    i = gen_block(i, table, gen)
    
    gen.add(var_name, 'l-val')
    gen.add(var_name, 'r-val')
    gen.add(step_val, 'int')
    gen.add('+', 'math_op')
    gen.add(':=', 'assign_op')
    
    gen.add(m_start, 'label')
    gen.add('JMP', 'jump')
    
    gen.set_label(m_end)
    gen.add(m_end, 'label')
    gen.add(':', 'colon')
    
    return i


def gen_while(start, table, gen):
    i = start + 1
    
    m_start = gen.generate_label()
    m_end = gen.generate_label()
    
    gen.set_label(m_start)
    gen.add(m_start, 'label')
    gen.add(':', 'colon')
    
    _, lex, tok, _ = table[i]
    if lex == '(':
        i += 1
    
    i = gen_expr(i, table, gen, until=[')'])
    
    if i <= len(table):
        i += 1
    
    gen.add(m_end, 'label')
    gen.add('JF', 'jf')
    
    i = gen_block(i, table, gen)
    
    gen.add(m_start, 'label')
    gen.add('JMP', 'jump')
    
    gen.set_label(m_end)
    gen.add(m_end, 'label')
    gen.add(':', 'colon')
    
    return i


def gen_do_while(start, table, gen):
    i = start + 1
    
    m_start = gen.generate_label()
    m_end = gen.generate_label()
    
    gen.set_label(m_start)
    gen.add(m_start, 'label')
    gen.add(':', 'colon')
    
    i = gen_block(i, table, gen)
    
    if i > len(table):
        return i
    
    _, lex, tok, _ = table[i]
    if lex == 'while':
        i += 1
        if i > len(table):
            return i
    
    _, lex, tok, _ = table[i]
    if lex == '(':
        i += 1
        if i > len(table):
            return i
    
    i = gen_expr(i, table, gen, until=[')'])
    if i > len(table):
        return i
    
    _, lex, tok, _ = table[i]
    if lex == ')':
        i += 1
        
    gen.add('NOT', 'bool_op')
    gen.add(m_end, 'label')
    gen.add('JF', 'jf')
    
    gen.add(m_start, 'label')
    gen.add('JMP', 'jump')
    
    gen.set_label(m_end)
    gen.add(m_end, 'label')
    gen.add(':', 'colon')
    
    return i


def gen_when(start, table, gen):
    i = start + 1
    
    _, lex, tok, _ = table[i]
    if lex == '(':
        i += 1
    
    i = gen_expr(i, table, gen, until=[')'])
    
    if i <= len(table):
        _, lex, tok, _ = table[i]
        if lex == ')':
            i += 1
    
    _, lex, tok, _ = table[i]
    if lex == '{':
        i += 1
    
    end_label = gen.generate_label()
    max_iterations = len(table)
    iterations = 0
    
    while i <= len(table):
        iterations += 1
        if iterations > max_iterations:
            print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Можливий нескінченний цикл в gen_when на позиції {i}")
            break
        
        _, lex, tok, _ = table[i]
        
        if lex == '}':
            i += 1
            break
        
        if lex == 'else' and tok == 'keyword':
            i += 1
            _, lex, tok, _ = table[i]
            if lex == '->':
                i += 1
            gen.add('POP', 'stack_op')
            old_i = i
            i = gen_when_branch_body(i, table, gen)
            if i == old_i:
                i += 1
            gen.add(end_label, 'label')
            gen.add('JMP', 'jump')
            continue
        
        next_label = gen.generate_label()
        match_label = gen.generate_label()
        
        gen.add('DUP', 'stack_op')
        
        first_value = True
        value_iterations = 0
        while True:
            value_iterations += 1
            if value_iterations > 100:
                print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Забагато значень в when на позиції {i}")
                break
            
            if not first_value:
                gen.add('DUP', 'stack_op')
            first_value = False
            
            old_i = i
            i = gen_when_value(i, table, gen)
            if i == old_i:
                print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Застряг при парсингу значення when на позиції {i}")
                i += 1
                break
            
            gen.add('==', 'rel_op')
            
            if i > len(table):
                break
            
            _, lex, tok, _ = table[i]
            
            if lex == ',':
                gen.add(match_label, 'label')
                gen.add('JF', 'jf')
                i += 1
                continue
            elif lex == '->':
                break
            else:
                break
        
        gen.set_label(match_label)
        gen.add(match_label, 'label')
        gen.add(':', 'colon')
        
        if i <= len(table):
            _, lex, tok, _ = table[i]
            if lex == '->':
                i += 1
        
        gen.add(next_label, 'label')
        gen.add('JF', 'jf')
        
        gen.add('POP', 'stack_op')
        old_i = i
        i = gen_when_branch_body(i, table, gen)
        if i == old_i:
            i += 1
        
        gen.add(end_label, 'label')
        gen.add('JMP', 'jump')
        
        gen.set_label(next_label)
        gen.add(next_label, 'label')
        gen.add(':', 'colon')
    
    gen.add('POP', 'stack_op')
    
    gen.set_label(end_label)
    gen.add(end_label, 'label')
    gen.add(':', 'colon')
    
    return i


def gen_when_value(start, table, gen):
    i = start
    if i > len(table):
        return i
    
    _, lex, tok, _ = table[i]
    
    if tok == 'identifier':
        gen.add(lex, 'r-val')
        return i + 1
    elif tok in ('int_const', 'real_const', 'bool_const'):
        typ_map = {'int_const': 'int', 'real_const': 'float', 'bool_const': 'bool'}
        gen.add(lex, typ_map[tok])
        return i + 1
    elif tok == 'string_const':
        gen.add(f'"{lex}"', 'string')
        return i + 1
    else:
        return gen_expr(i, table, gen, until=[',', '->'])


def gen_when_branch_body(start, table, gen):
    i = start
    if i > len(table):
        return i
    
    _, lex, tok, _ = table[i]
    
    if lex == '{':
        i += 1
        brace_count = 1
        max_iterations = len(table) * 2
        iterations = 0
        
        while i <= len(table) and brace_count > 0:
            iterations += 1
            if iterations > max_iterations:
                print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Можливий нескінченний цикл в gen_when_branch_body на позиції {i}")
                break
            
            _, lex, tok, _ = table[i]
            if lex == '{':
                brace_count += 1
                i += 1
            elif lex == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
                i += 1
            else:
                old_i = i
                i = process_statement(i, table, gen)
                if i == old_i:
                    print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Застряг в when branch body на позиції {i}")
                    i += 1
        return i + 1
    else:
        return process_statement(i, table, gen)


def gen_print(start, table, gen):
    i = start + 1
    
    _, lex, tok, _ = table[i]
    if lex == '(':
        i += 1
    
    _, lex, tok, _ = table[i]
    if lex != ')':
        i = gen_expr(i, table, gen, until=[')'])
    
    gen.add('OUT', 'out_op')
    
    if i <= len(table):
        i += 1
    
    return i


def gen_block(start, table, gen):
    i = start
    if i > len(table):
        return i
    
    _, lex, tok, _ = table[i]
    
    if lex == '{':
        i += 1
        brace_count = 1
        max_iterations = len(table) * 2
        iterations = 0
        
        while i <= len(table) and brace_count > 0:
            iterations += 1
            if iterations > max_iterations:
                print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Можливий нескінченний цикл в gen_block на позиції {i}")
                break
            
            _, lex, tok, _ = table[i]
            if lex == '{':
                brace_count += 1
                i += 1
            elif lex == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
                i += 1
            else:
                old_i = i
                i = process_statement(i, table, gen)
                if i == old_i:
                    print(f"\n⚠️ ПОПЕРЕДЖЕННЯ: Застряг в блоці на позиції {i}")
                    i += 1
        return i + 1
    else:
        return process_statement(i, table, gen)


def compile_to_postfix(filename="test"):
    print("\n" + "="*60)
    print("КОМПІЛЯЦІЯ У ПОСТФІКС-КОД")
    print("="*60)
    
    if not lex_qirim.FSuccess[1]:
        print("ПОМИЛКА: Лексичний аналіз не пройшов успішно!")
        return False
    
    print("✓ Лексичний аналіз завершено")
    print("✓ Синтаксичний та семантичний аналіз завершено")
    
    print("\nГенерація постфікс-коду...")
    
    try:
        generate_simple_postfix()
        print("✓ Генерація постфікс-коду завершена")
        
        print_postfix_code()
        save_postfix_to_file(filename)
        
        generate_function_postfix_files(filename)
        
        return True
        
    except Exception as e:
        print(f"\nПОМИЛКА при генерації постфікс-коду: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_function_postfix_files(base_filename):
    """Генерує окремі .postfix файли для кожної функції"""
    if not hasattr(syntax_qirim, 'tableOfFunc') or not syntax_qirim.tableOfFunc:
        return
    
    tableOfSymb = lex_qirim.tableOfSymb
    
    for func_name, func_info in syntax_qirim.tableOfFunc.items():
        if func_name == 'main':
            continue
        
        print(f"\nГенерація постфікс-коду для функції {func_name}...")
        
        func_start = None
        func_end = None
        brace_depth = 0
        
        for i in range(1, len(tableOfSymb) + 1):
            numLine, lex, tok, idx = tableOfSymb[i]
            
            if tok == 'keyword' and lex == 'fun':
                if i + 1 <= len(tableOfSymb):
                    _, next_lex, _, _ = tableOfSymb[i + 1]
                    if next_lex == func_name:
                        func_start = i
                        continue
            
            if func_start is not None and func_end is None:
                if tok == 'brackets_op':
                    if lex == '{':
                        brace_depth += 1
                    elif lex == '}':
                        brace_depth -= 1
                        if brace_depth == 0:
                            func_end = i
                            break
        
        if func_start is None or func_end is None:
            print(f"⚠️ ПОПЕРЕДЖЕННЯ: Не знайдено тіло функції {func_name}")
            continue
        
        generator = PostfixGenerator()
        
        i = func_start
        while i <= func_end:
            _, lex, tok, _ = tableOfSymb[i]
            
            if tok == 'keyword' and lex == 'fun':
                i += 1
                continue
            
            if tok == 'identifier' and lex == func_name:
                i += 1
                continue
            
            if tok == 'brackets_op' and lex == '(':
                while i <= func_end:
                    _, lex, tok, _ = tableOfSymb[i]
                    if lex == ')':
                        break
                    i += 1
                i += 1
                continue
            
            if tok == 'punct' and lex == ':':
                i += 1
                if i <= func_end:
                    _, lex, tok, _ = tableOfSymb[i]
                    if tok == 'keyword':
                        i += 1
                continue
            
            if tok == 'assign_op' and lex == '=':
                i += 1
                i = gen_expr(i, tableOfSymb, generator, until=[';', '}'])
                generator.add('RET', 'RET')
                break
            
            if tok == 'brackets_op' and lex == '{':
                i += 1
                brace_count = 1
                while i <= func_end and brace_count > 0:
                    _, lex, tok, _ = tableOfSymb[i]
                    if lex == '{':
                        brace_count += 1
                        i += 1
                    elif lex == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            break
                        i += 1
                    else:
                        old_i = i
                        i = process_statement(i, tableOfSymb, generator)
                        if i == old_i:
                            i += 1
                generator.add('RET', 'RET')
                break
            
            i += 1
        
        save_function_postfix_file(base_filename, func_name, generator, func_info)


def save_function_postfix_file(base_filename, func_name, generator, func_info):
    """Зберігає .postfix файл для окремої функції"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    filepath = os.path.join(OUTPUT_DIR, f"{base_filename}${func_name}.postfix")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(".target: Postfix Machine\n")
        f.write(".version: 0.2\n")
        
        f.write(".vars(\n")
        
        if hasattr(syntax_qirim, 'tableOfVarByFunction') and func_name in syntax_qirim.tableOfVarByFunction:
            func_vars = syntax_qirim.tableOfVarByFunction[func_name]
            for var_name, var_info in func_vars.items():
                if isinstance(var_info, dict) and 'type' in var_info:
                    var_type = var_info['type'].lower()
                elif isinstance(var_info, str):
                    var_type = var_info.lower()
                else:
                    var_type = str(var_info).lower()
                
                if var_type == 'real':
                    var_type = 'float'
                elif var_type == 'boolean':
                    var_type = 'bool'
                
                f.write(f"{var_name} {var_type}\n")
        
        all_vars_in_postfix = {}
        for lex, tok in generator.postfix:
            if tok == 'l-val':
                if lex not in all_vars_in_postfix:
                    all_vars_in_postfix[lex] = 'int'
        
        for var_name in all_vars_in_postfix:
            found = False
            if hasattr(syntax_qirim, 'tableOfVarByFunction') and func_name in syntax_qirim.tableOfVarByFunction:
                if var_name in syntax_qirim.tableOfVarByFunction[func_name]:
                    found = True
            if not found:
                f.write(f"{var_name} int\n")
        
        f.write(")\n")
        
        f.write(".funcs(\n")
        f.write(")\n")
        
        f.write(".globVarList(\n")
        f.write(")\n")
        
        f.write(".labels(\n")
        for label_name, label_value in generator.labels.items():
            if label_value != 'val_undef':
                f.write(f"{label_name} {label_value}\n")
        f.write(")\n")
        
        f.write(".constants(\n")
        f.write(")\n")
        
        f.write(".code(\n")
        for lex, tok in generator.postfix:
            f.write(f"{lex} {tok}\n")
        f.write(")\n")
    
    print(f"✓ Функція {func_name} збережена у файл: {filepath}")


if __name__ == "__main__":
    if lex_qirim.FSuccess[1]:
        compile_to_postfix("test")