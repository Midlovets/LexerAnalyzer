tokenTable = {
    # Ключові слова
    'fun': 'keyword', 'main': 'keyword', 'val': 'keyword', 'var': 'keyword',
    'if': 'keyword', 'else': 'keyword', 'when': 'keyword', 'for': 'keyword',
    'do': 'keyword', 'while': 'keyword', 'return': 'keyword', 'continue': 'keyword',
    'break': 'keyword', 'is': 'keyword', 'in': 'keyword', 'downTo': 'keyword',
    'step': 'keyword', 'readLine': 'keyword', 'print': 'keyword',

    # Типи даних
    'Int': 'type', 'Real': 'type', 'String': 'type', 'Boolean': 'type', 'Unit': 'type',

    # Логічні константи
    'true': 'bool_const', 'false': 'bool_const',

    # Оператори
    '=': 'assign_op',
    '+': 'add_op', '-': 'add_op',
    '*': 'mult_op', '/': 'mult_op', '%': 'mult_op',
    '**': 'exp_op',
    '==': 'rel_op', '!=': 'rel_op', '<': 'rel_op', '>': 'rel_op', '<=': 'rel_op', '>=': 'rel_op',
    '&&': 'logical_op', '||': 'logical_op', '!': 'logical_op',

    # Роздільники та дужки
    '(': 'brackets_op', ')': 'brackets_op', '{': 'brackets_op', '}': 'brackets_op',
    '.': 'punct', ',': 'punct', ':': 'punct', ';': 'punct', '?': 'punct',
    "'": "punct", '"': 'punct', '`': 'punct', '->': 'punct', '..': 'punct',
}

tokStateTable = {
    2: 'identifier',  # Стан 2 - ідентифікатори (звичайні)
    5: 'real_const',  # Стан 5 - дійсні числа
    6: 'int_const',  # Стан 6 - цілі числа
    9: 'identifier',  # Стан 9 - лапкові ідентифікатори (`...`)
    12: 'string_const'  # Стан 12 - рядок
}

# Діаграма станів
stf = {
    # Стан 0 - початковий стан
    (0, 'ws'): 0,
    (0, 'Letter'): 1, (0, '_'): 1,
    (0, 'Digit'): 3,
    (0, '`'): 7,
    (0, '"'): 10,
    (0, '='): 13,
    (0, '.'): 14, (0, ','): 14, (0, '->'): 14, (0, ';'): 14, (0, ':'): 14, (0, '?'): 14, (0, '..'): 14,
    (0, '+'): 15, (0, '-'): 15, (0, '*'): 15, (0, '/'): 15, (0, '**'): 15,
    (0, '('): 16, (0, ')'): 16, (0, '{'): 16, (0, '}'): 16,
    (0, '&&'): 17, (0, '||'): 17, (0, '!'): 17,
    (0, '<'): 18, (0, '<='): 18, (0, '>'): 18, (0, '>='): 18, (0, '=='): 18, (0, '!='): 18,
    (0, 'nl'): 19,
    (0, '//'): 20,

    # Стан 1 - читання ідентифікатора
    (1, 'Letter'): 1, (1, 'Digit'): 1, (1, '_'): 1,
    (1, 'other'): 2,

    # Стан 3 - читання цілого числа
    (3, 'Digit'): 3,
    (3, '.'): 4,
    (3, 'other'): 6,
    (3, 'Letter'): 101,

    # Стан 4 - що може бути після крапки
    (4, 'Digit'): 4,
    (4, 'other'): 5,
    (4, 'Letter'): 101,

    # Стан 10 - початок рядка
    (10, '"'): 12,
    (10, 'other'): 11, (10, 'nl'): 11, (10, 'ws'): 11,

    # Стан 11 - читання рядка
    (11, '"'): 12,
    (11, 'other'): 11, (11, 'nl'): 11, (11, 'ws'): 11,

    # Стан 7 - початок ідентифікатора у лапках `
    (7, 'Letter'): 8, (7, 'Digit'): 8, (7, 'other'): 8,
    (7, '`'): 101,  # пустий `...` - помилка

    # Стан 8 - усередині лапкового ідентифікатора
    (8, 'Letter'): 8, (8, 'Digit'): 8, (8, 'other'): 8,
    (8, '`'): 9,
    (8, 'nl'): 101,

    # Коментар
    (20, 'other'): 20,
    (20, 'nl'): 21,

    # Загальний перехід для помилок
    (0, 'other'): 101,
}

# Односимвольні оператори (ліворуч) - використовується після перевірки двосимвольних операторів
single_char_tokens = {
    '+': 'add_op', '-': 'add_op',
    '*': 'mult_op', '/': 'mult_op', '%': 'mult_op',
    '(': 'brackets_op', ')': 'brackets_op', '{': 'brackets_op', '}': 'brackets_op',
    ',': 'punct', ':': 'punct', ';': 'punct', '?': 'punct', "'": 'punct',
    '=': 'assign_op', '!': 'logical_op', '<': 'rel_op', '>': 'rel_op'
}

# Двосимвольні оператори/послідовності, які треба перевіряти першими
multi_char_tokens = {
    '**': 'exp_op', '==': 'rel_op', '!=': 'rel_op', '<=': 'rel_op', '>=': 'rel_op',
    '&&': 'logical_op', '||': 'logical_op', '->': 'punct', '..': 'punct', '//': 'comment'
}

initState = 0
# F - всі фінальні стани
F = {2, 5, 6, 9, 12, 13, 14, 15, 16, 17, 18, 19, 21, 101}
# Fstar - фінальні стани, де останній символ має бути повернений назад (не включає закриття лапок/`-ідентифікатор)
Fstar = {2, 5, 6}
Ferror = {101}

tableOfId = {}
tableOfConst = {}
tableOfSymb = {}

state = initState
FSuccess = ('Lexer', False)

with open('test.qirim', 'r', encoding='utf-8') as file:
    sourceCode = file.read()

lenCode = len(sourceCode)
numLine = 1
numChar = -1
char = ''
lexeme = ''


# Погляд на наступний символ без просування
def peekChar():
    if numChar + 1 < lenCode:
        return sourceCode[numChar + 1]
    return ''


def lex():
    global state, numLine, char, lexeme, numChar, FSuccess

    try:
        while numChar < lenCode - 1:
            char = nextChar()
            # Якщо новий рядок - збільшуємо номер рядка, але не пропускаємо символ якщо ми не у стартовому стані (щоб рядки та ін. могли містити nl, де дозволено)
            classCh = classOfChar(char)
            if classCh == 'nl':
                numLine += 1
                if state == 0:
                    continue
                # Інакше - обробляємо як звичайний символ (потрапляє в стани, де дозволено nl)

            if classCh == 'ws' and state == 0:
                continue

            # Якщо стартовий стан - спробуємо спочатку двосимвольні оператори (lookahead)
            if state == 0:
                # Пропускаємо пробіли в початковому стані
                if classCh == 'ws':
                    continue
                nxt = peekChar()
                two = char + nxt if nxt else ''
                if two in multi_char_tokens:
                    if two == '//':
                        nextChar()
                        state = 20
                        lexeme = '//'
                        # Далі цикл продовжиться і додаватиме символи коментаря до nl
                        continue
                    else:
                        # Двосимвольний оператор -> виводимо відразу як токен
                        lexeme = two
                        token = multi_char_tokens[two] if two in multi_char_tokens else tokenTable.get(two, 'unknown')
                        print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                        lexeme = ''
                        nextChar()
                        continue

                # Якщо односимвольний символ, але ми вирішили його розпізнати одразу (оператори, дужки, пунктуація)
                if char in single_char_tokens:
                    # Однак можливі випадки коли символ '.' окрема обробка
                    lexeme = char
                    token = single_char_tokens[char]
                    print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                    tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                    lexeme = ''
                    continue

            # Спеціальна обробка для оператора .. (коли ми в стані 3 - після цілого числа)
            if state == 3 and char == '.':
                # Перевіряємо, чи наступний символ теж крапка
                nxt = peekChar()
                if nxt == '.':
                    state = 6
                    processing()  # Обробляємо як ціле число
                    nextChar()  # Тепер обробляємо оператор ..
                    lexeme = '..'
                    token = multi_char_tokens['..']
                    print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                    tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                    lexeme = ''
                    state = initState
                    continue
                else:
                    # Це дійсне число з крапкою - переходимо в стан 4
                    state = 4
                    lexeme += char
                    continue

            # Спеціальна обробка для оператора .. (коли ми в стані 4 - після крапки в числі)
            if state == 4 and char == '.':
                # Перевіряємо, чи наступний символ теж крапка
                nxt = peekChar()
                if nxt == '.':
                    # Видаляємо крапку з лексеми (оскільки це було помилкове розуміння)
                    if lexeme.count('.') == 1 and lexeme.split('.')[-1].isdigit():
                        state = 5
                        processing()
                        nextChar()  # з'їдаємо другий символ '.'
                        lexeme = '..'
                        token = multi_char_tokens['..']
                        print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                        lexeme = ''
                        state = initState
                        continue
                    else:
                        if lexeme.endswith('.'):
                            lexeme = lexeme[:-1]
                        state = 6
                        processing()
                        nextChar()  # з'їдаємо другий символ '.'
                        lexeme = '..'
                        token = multi_char_tokens['..']
                        print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                        lexeme = ''
                        state = initState
                        continue
                else:
                    lexeme += char
                    continue

            if state == 0 and char in ['.', '-', '>']:
                nxt = peekChar()
                if char == '.' and nxt == '.':
                    # Оператор ..
                    nextChar()
                    lexeme = '..'
                    token = multi_char_tokens['..']
                    print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                    tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                    lexeme = ''
                    continue
                elif char == '-' and nxt == '>':
                    # Оператор ->
                    nextChar()
                    lexeme = '->'
                    token = multi_char_tokens['->']
                    print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                    tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                    lexeme = ''
                    continue

            state = next_state(state, classCh)

            if state in (9, 12):
                lexeme += char
                processing()
                continue

            if state in Ferror:
                lexeme += char
                fail()
                return

            if is_final(state):
                processing()
            elif state == initState:
                lexeme = ''
            else:
                lexeme += char

        if state != initState and state not in F:
            print(f'Лексер: у рядку {numLine} незавершена лексема "{lexeme}"')
            FSuccess = ('Lexer', False)
            return

        print('Лексер: Лексичний аналіз завершено успішно')
        FSuccess = ('Lexer', True)
    except SystemExit as e:
        print(f'Лексер: Аварійне завершення програми з кодом {e}')
        FSuccess = ('Lexer', False)


def processing():
    global state, lexeme, char, numLine, numChar, tableOfSymb

    # Якщо сучасний стан - один з тих, що породжують токен-ідентифікатор/константу
    if state in (2, 5, 6, 9, 12):
        # Перевіряємо, чи лексема не порожня
        if not lexeme:
            lexeme = ''
            state = initState
            return

        token = getToken(state, lexeme)
        if token in ('identifier', 'int_const', 'real_const', 'string_const'):
            index = indexIdConst(state, lexeme)
            print('{0:<3d} {1:<15s} {2:<15s} {3:<5}'.format(numLine, lexeme, token, index))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:
            print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')

        lexeme = ''
        if state in Fstar:
            numChar = put_char_back(numChar)
        state = initState
        return

    # Для коментаря (стан 21 - фінал коментаря)
    if state == 21:
        # lexeme вже містить весь коментар (без nl)
        token = 'comment'
        print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
        return

    if state in F:
        if not lexeme:
            lexeme = ''
            state = initState
            return

        token = getToken(state, lexeme)
        print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
        return


def fail():
    global state, numLine, char, lexeme, FSuccess
    FSuccess = ('Lexer', False)

    if state == 101:
        print(f'{numLine:<3d} {lexeme:<15s} {"UNKNOWN":<15s} {"ERROR":<5s}')

        if lexeme and lexeme[0].isdigit() and any(c.isalpha() for c in lexeme):
            print(f'Лексер: у рядку {numLine} ідентифікатор не може починатися з цифр')
        elif is_cyrillic(char):
            print(f'Лексер: у рядку {numLine} неочікуваний символ кирилиці "{char}"')
        elif char == '@':
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}"')
        elif char in '#$%^&~':
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}"')
        else:
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}"')

        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, 'UNKNOWN', 'ERROR')
        return


def is_cyrillic(char):
    return '\u0400' <= char <= '\u04FF' or '\u0500' <= char <= '\u052F'


def is_final(state):
    return state in F


def next_state(state, class_ch):
    try:
        return stf[(state, class_ch)]
    except KeyError:
        if (state, 'other') in stf:
            return stf[(state, 'other')]
        else:
            return 101


def nextChar():
    global numChar
    numChar += 1
    if numChar < len(sourceCode):
        return sourceCode[numChar]
    return ''


def put_char_back(cur_num_char):
    return cur_num_char - 1


def classOfChar(ch):
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


def getToken(state, lexeme):
    if lexeme in tokenTable:
        return tokenTable[lexeme]
    if state in tokStateTable:
        return tokStateTable[state]
    return 'unknown'


def indexIdConst(state, lexeme):
    if state in (2, 9):  # звичайні та лапкові ідентифікатори
        if lexeme not in tableOfId:
            tableOfId[lexeme] = len(tableOfId) + 1
        return tableOfId[lexeme]

    elif state in (5, 6, 12):
        if lexeme not in tableOfConst:
            tableOfConst[lexeme] = len(tableOfConst) + 1
        return tableOfConst[lexeme]

    return 0


# Запуск аналізатора
if __name__ == '__main__':
    print("=== ЛЕКСИЧНИЙ АНАЛІЗ ПРОГРАМИ НА МОВІ QIRIM ===")
    print("Рядок Лексема         Токен           Індекс")
    print("-" * 55)

    lex()

    # Виведення таблиць
    if FSuccess[1]:
        print('\n' + '=' * 60)
        print('ТАБЛИЦІ:')
        print('=' * 60)
        print('Таблиця символів програми:')
        for key, value in tableOfSymb.items():
            print(f'{key}: {value}')

        print('\nТаблиця ідентифікаторів:')
        for key, value in tableOfId.items():
            print(f'{value}: {key}')

        print('\nТаблиця констант:')
        for key, value in tableOfConst.items():
            print(f'{value}: {key}')
    else:
        print('\n' + '=' * 60)
        print('АНАЛІЗ ЗАВЕРШЕНО З ПОМИЛКОЮ!')
        print('=' * 60)
