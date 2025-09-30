from prettytable import PrettyTable

tokenTable = {
    'fun': 'keyword', 'main': 'keyword', 'val': 'keyword', 'var': 'keyword',
    'if': 'keyword', 'else': 'keyword', 'when': 'keyword', 'for': 'keyword',
    'do': 'keyword', 'while': 'keyword', 'return': 'keyword', 'continue': 'keyword',
    'break': 'keyword', 'is': 'keyword', 'in': 'keyword', 'downTo': 'keyword',
    'step': 'keyword', 'readLine': 'keyword', 'print': 'keyword',

    'Int': 'type', 'Real': 'type', 'String': 'type', 'Boolean': 'type', 'Unit': 'type',

    'true': 'bool_const', 'false': 'bool_const',

    '=': 'assign_op',
    '+': 'add_op', '-': 'add_op',
    '*': 'mult_op', '/': 'mult_op', '%': 'mult_op',
    '**': 'exp_op',
    '==': 'rel_op', '!=': 'rel_op', '<': 'rel_op', '>': 'rel_op', '<=': 'rel_op', '>=': 'rel_op',
    '&&': 'logical_op', '||': 'logical_op', '!': 'logical_op',

    '(': 'brackets_op', ')': 'brackets_op', '{': 'brackets_op', '}': 'brackets_op',
    '.': 'punct', ',': 'punct', ':': 'punct', ';': 'punct', '?': 'punct',
    "'": "punct", '"': 'punct', '`': 'punct', '->': 'punct', '..': 'punct',

    ' ': 'ws', '\t': 'ws', '\f': 'ws',

    '\n': 'nl', '\r': 'nl', '\r\n': 'nl',
}

tokStateTable = {
    2: 'identifier',
    5: 'real_const',
    6: 'int_const',
    9: 'identifier',
    11: 'string_const',
}

# Діаграма станів
stf = {
    (0, 'ws'): 0,
    (0, 'Letter'): 1, (0, '_'): 1,
    (0, 'Digit'): 3,
    (0, '`'): 7,
    (0, '"'): 10,
    (0, '='): 12,
    (0, ','): 15, (0, '+'): 15, (0, '%'): 15, (0, ';'): 15, (0, ':'): 15, (0, '?'): 15,
    (0, '('): 15, (0, ')'): 15, (0, '{'): 15, (0, '}'): 15,
    (0, '*'): 16,
    (0, '&'): 19,
    (0, '|'): 21,
    (0, '!'): 23,
    (0, 'nl'): 27,
    (0, '<'): 28,
    (0, '>'): 28,
    (0, '/'): 31,
    (0, '-'): 35,
    (0, '.'): 39,

    (1, 'Letter'): 1, (1, 'Digit'): 1, (1, '_'): 1,
    (1, 'other'): 2,

    (3, 'Digit'): 3,
    (3, '.'): 4,
    (3, 'other'): 6,

    (4, 'Digit'): 26,
    (4, '.'): 38,

    (7, 'Letter'): 8, (7, 'Digit'): 8, (7, 'other'): 8,
    (7, 'nl'): 104, (7, '`'): 104,

    (8, 'Letter'): 8, (8, 'Digit'): 8, (8, 'other'): 8,
    (8, '`'): 9,
    (8, 'nl'): 104,

    (10, 'other'): 10, (10, 'nl'): 104, (10, 'ws'): 10,
    (10, '"'): 11,

    (12, 'other'): 13,
    (12, '='): 14,

    (16, '*'): 17,
    (16, 'other'): 18,

    (19, '&'): 20,
    (19, 'other'): 102,

    (21, '|'): 22,
    (21, 'other'): 103,

    (23, '='): 24,
    (23, 'other'): 25,

    (26, 'Digit'): 26,
    (26, '.'): 26,
    (26, 'other'): 5,

    (28, 'other'): 29,
    (28, '='): 30,

    (35, 'other'): 36,
    (35, '>'): 37,

    (31, 'other'): 32,
    (31, '/'): 33,

    (33, 'Letter'): 33, (33, 'Digit'): 33, (33, 'other'): 33,
    (33, 'nl'): 34,

    (39, '.'): 40,
    (39, 'Digit'): 26,
    (39, 'other'): 105,

    (0, 'other'): 101,
}

initState = 0
# F - всі фінальні стани
F = {2, 5, 6, 9, 11, 13, 14, 15, 17, 18, 20, 22, 24, 25, 27, 29, 30, 32, 34, 36, 37, 38, 40, 101, 102, 103, 104, 105}
# Fstar - фінальні стани, де останній символ має бути повернений назад
Fstar = {2, 5, 6, 13, 18, 25, 29, 32, 36}
Ferror = {101, 102, 103, 104, 105}

tableOfId = {}
tableOfConst = {}
tableOfSymb = {}

state = initState
FSuccess = ('Lexer', False)
statusMessage = ''
lexemeStartLine = 1

with open('test.qirim', 'r', encoding='utf-8') as file:
    sourceCode = file.read()

lenCode = len(sourceCode)
numLine = 1
numChar = -1
char = ''
lexeme = ''


def lex():
    global state, numLine, char, lexeme, numChar, FSuccess, statusMessage, lexemeStartLine
    while numChar < lenCode - 1:
        char = next_char()
        class_ch = class_of_char(char)
        if class_ch == 'nl':
            if state == initState:
                numLine += 1
                continue
            if state in (10, 33):
                numLine += 1
        if class_ch == 'ws' and state == initState:
            continue
        prev_state = state
        state = next_state(state, class_ch)
        if prev_state == initState and state != initState:
            lexemeStartLine = numLine
        if state in Ferror:
            lexeme += char
            if prev_state == 10 and state == 104:
                token = 'string_const'
                index = index_id_const(11, lexeme[:-1])
                tableOfSymb[len(tableOfSymb) + 1] = (lexemeStartLine, lexeme[:-1], token, index)
                statusMessage = f"\nАВАРІЙНЕ ЗАВЕРШЕННЯ ПРОГРАМИ! Незавершена лексема у рядку {lexemeStartLine}."
                FSuccess = ('Lexer', False)
                return
            fail()
            return
        if is_final(state):
            if state in Fstar:
                processing()
            else:
                lexeme += char
                processing()
            continue
        if state == initState:
            lexeme = ''
        else:
            lexeme += char
    statusMessage = '\nЛексичний аналіз завершено успішно!\n'
    FSuccess = ('Lexer', True)


def processing():
    global state, lexeme, char, numLine, numChar, tableOfSymb
    if not lexeme:
        state = initState
        return
    if state == 38 and lexeme.endswith('..') and len(lexeme) > 2:
        left = lexeme[:-2]
        if left.replace('.', '', 1).isdigit():
            if '.' in left:
                token = 'real_const'
                index = index_id_const(5, left)
            else:
                token = 'int_const'
                index = index_id_const(6, left)
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, left, token, index)
            numChar = put_char_back(put_char_back(numChar))
            lexeme = ''
            state = initState
            return
    if state in (2, 5, 6, 9, 11):
        token = get_token(state, lexeme)
        if token in ('identifier', 'int_const', 'real_const', 'string_const'):
            index = index_id_const(state, lexeme)
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        if state in Fstar:
            numChar = put_char_back(numChar)
        state = initState
        return
    if state == 34:
        lexeme = ''
        state = initState
        return
    if state in F:
        token = get_token(state, lexeme)
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        if state in Fstar:
            numChar = put_char_back(numChar)
        state = initState
        return


def fail():
    global state, numLine, char, lexeme, FSuccess, statusMessage
    FSuccess = ('Lexer', False)
    tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, 'UNKNOWN', 'ERROR')
    # Помилки з кодом 102–105
    if state == 102:
        statusMessage = f'\nПОМИЛКА! У рядку {numLine} очікувався &&.'
        return
    if state == 103:
        statusMessage = f'\nПОМИЛКА! У рядку {numLine} очікувався ||.'
        return
    if state == 104:
        statusMessage = f'\nПОМИЛКА! У рядку {numLine} неправильне оголошення ідентифікатора у зворотних лапках.'
        return
    if state == 105:
        statusMessage = f'\nПОМИЛКА! У рядку {numLine} очікувалось .. або число.'
        return
    # Загальна помилка з кодом 101
    if lexeme and lexeme[0].isdigit() and any(c.isalpha() for c in lexeme):
        statusMessage = f'\nПОМИЛКА! У рядку {numLine} після крапки МОЖЕ йти тільки цифра або крапка.'
    elif is_cyrillic(char):
        statusMessage = f'\nПОМИЛКА! У рядку {numLine} неочікуваний символ кирилиці "{char}".'
    else:
        statusMessage = f'\nПОМИЛКА! У рядку {numLine} неочікуваний символ "{char}".'


def is_cyrillic(character):
    return '\u0400' <= character <= '\u04FF' or '\u0500' <= character <= '\u052F'


def is_final(state):
    return state in F


def next_state(state, class_ch):
    try:
        return stf[(state, class_ch)]
    except KeyError:
        return stf[(state, 'other')]


def next_char():
    global numChar
    numChar += 1
    return sourceCode[numChar]


def put_char_back(cur_num_char):
    return cur_num_char - 1


def class_of_char(ch):
    if ch == '.':
        return '.'
    elif ch == '_':
        return '_'
    elif ch.isalpha() and not is_cyrillic(ch):
        return "Letter"
    elif is_cyrillic(ch):
        return "other"
    elif ch.isdigit():
        return "Digit"
    elif ch in " \t\f":
        return "ws"
    elif ch in "\n\r":
        return "nl"
    elif ch == '"':
        return '"'
    elif ch == '`':
        return '`'
    elif ch in "+-*/(){},:;?'=!<>&|%":
        return ch
    else:
        return 'other'


def get_token(state, lexeme):
    if lexeme in tokenTable:
        return tokenTable[lexeme]
    if state in tokStateTable:
        return tokStateTable[state]
    return 'unknown'


def index_id_const(state, lexeme):
    if state in (2, 9):
        if lexeme not in tableOfId:
            tableOfId[lexeme] = len(tableOfId) + 1
        return tableOfId[lexeme]
    elif state in (5, 6, 11, 12):
        if lexeme not in tableOfConst:
            tableOfConst[lexeme] = len(tableOfConst) + 1
        return tableOfConst[lexeme]
    return 0


def _fmt_cell_lexeme(text, max_len=60):
    s = '' if text is None else str(text)
    if '\n' in s or '\r' in s:
        s = s.splitlines()[0]
    s = s.replace('\t', ' ')
    if len(s) > max_len:
        return s[:max_len - 1] + '…'
    return s


if __name__ == '__main__':
    lex()
    print("\nЛЕКСИЧНИЙ АНАЛІЗ ПРОГРАМИ МОВОЮ QIRIM")

    main_tbl = PrettyTable()
    main_tbl.field_names = ["Рядок", "Лексема", "Токен", "Індекс"]
    for _, (ln, lex, tok, idx) in tableOfSymb.items():
        main_tbl.add_row([ln, _fmt_cell_lexeme(lex), tok, idx])
    print(main_tbl)
    print(statusMessage)
    if FSuccess[1]:
        print('ТАБЛИЦІ:')

        symb = PrettyTable()
        symb.field_names = ["№", "Лексема", "Токен", "Індекс"]
        for key, (ln, lex, tok, idx) in tableOfSymb.items():
            symb.add_row([key, _fmt_cell_lexeme(lex), tok, idx])
        print('Таблиця символів програми:')
        print(symb)

        ids = PrettyTable()
        ids.field_names = ["Індекс", "Ідентифікатор"]
        for lex, idx in sorted(tableOfId.items(), key=lambda x: x[1]):
            ids.add_row([idx, _fmt_cell_lexeme(lex)])
        print('\nТаблиця ідентифікаторів:')
        print(ids)

        consts = PrettyTable()
        consts.field_names = ["Індекс", "Константа"]
        for lex, idx in sorted(tableOfConst.items(), key=lambda x: x[1]):
            consts.add_row([idx, _fmt_cell_lexeme(lex)])
        print('\nТаблиця констант:')
        print(consts)
