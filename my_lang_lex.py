# Лексичний аналізатор для мови програмування Qirim
# Таблиця лексем мови Qirim
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
    '==': 'rel_op', '!=': 'rel_op', '<': 'rel_op', '>': 'rel_op',
    '<=': 'rel_op', '>=': 'rel_op',
    '&&': 'logical_op', '||': 'logical_op', '!': 'logical_op',

    # Роздільники і дужки
    '(': 'brackets_op', ')': 'brackets_op', '{': 'brackets_op', '}': 'brackets_op',
    '.': 'punct', ',': 'punct', ':': 'punct', ';': 'punct', '?': 'punct',
    "'": "punct", '"': 'punct', '`': 'punct', '->': 'punct', '..': 'punct',

    # Пробільні символи
    '\t': 'ws', ' ': 'ws', '\f': 'ws', '\n': 'nl', '\r': 'nl'
}

# Решту токенів визначаємо не за лексемою, а за заключним станом
tokStateTable = {2: 'identifier', 6: 'real_const', 9: 'int_const', 11: 'string_const'}

# Діаграма станів для мови Qirim
# Стани:
# 0 - початковий стан
# 1 - читання ідентифікатора/ключового слова
# 2 - кінцевий стан ідентифікатора (з *)
# 3 - пропуск пробільних символів (повернення в стан 0)
# 4 - читання цілого числа
# 5 - читання дробової частини числа
# 6 - кінцевий стан дійсного числа (з *)
# 7 - початок рядкової константи
# 8 - читання вмісту рядка
# 9 - кінцевий стан цілого числа (з *)
# 10 - читання складених операторів (==, !=, <=, >=, &&, ||, **)
# 11 - кінцевий стан рядкової константи
# 12 - кінцевий стан складених операторів
# 13 - кінцевий стан нового рядка
# 14 - обробка крапки (може бути . або ..)
# 15 - обробка слешу (може бути / або //)
# 16 - перехід з числа в ідентифікатор (123x -> ідентифікатор)
# 17 - читання коментаря
# 20 - читання екранованого ідентифікатора
# 101 - стан помилок

stf = {
    # Ідентифікатори та ключові слова
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, '_'): 1,
    (1, 'other'): 2,

    # Числа
    (0, 'Digit'): 4, (4, 'Digit'): 4, (4, '_'): 4, (4, 'dot'): 5,
    # ВИПРАВЛЕННЯ: якщо після числа йде літера, це стає ідентифікатором
    (4, 'Letter'): 16, (4, '_'): 16, (4, 'other'): 9,
    (5, 'Digit'): 5, (5, '_'): 5,
    # ВИПРАВЛЕННЯ: якщо після дробового числа йде літера, це стає ідентифікатором
    (5, 'Letter'): 16, (5, 'other'): 6,

    # Новий стан для переходу з числа в ідентифікатор
    (16, 'Letter'): 16, (16, 'Digit'): 16, (16, '_'): 16, (16, 'other'): 2,

    # ВИПРАВЛЕНО: Рядкові константи
    (0, '"'): 8,  # Перехід відразу в стан читання рядка
    (8, '"'): 11,  # Закриваюча лапка завершує рядок
    (8, 'other'): 8,  # Будь-який інший символ продовжує рядок
    (8, 'nl'): 8,  # Новий рядок теж може бути частиною рядка
    (8, 'ws'): 8,  # Пробільні символи в рядку

    # Екрановані ідентифікатори
    (0, '`'): 20, (20, 'other'): 20, (20, '`'): 2,

    # Прості оператори
    (0, '+'): 12, (0, '-'): 12, (0, '*'): 10, (0, '/'): 15, (0, '%'): 12,
    (0, '('): 12, (0, ')'): 12, (0, '{'): 12, (0, '}'): 12,
    (0, '.'): 14, (0, ','): 12, (0, ':'): 12, (0, ';'): 12,
    (0, '?'): 12, (0, "'"): 12,

    # Складені оператори
    (0, '='): 10, (10, '='): 12,  # = або ==
    (0, '!'): 10, (10, '='): 12,  # ! або !=
    (0, '<'): 10, (10, '='): 12,  # < або <=
    (0, '>'): 10, (10, '='): 12,  # > або >=
    (0, '&'): 10, (10, '&'): 12,  # && (має бути два символи)
    (0, '|'): 10, (10, '|'): 12,  # || (має бути два символи)
    (10, '*'): 12,  # **
    (14, '.'): 12,  # ..
    (10, 'other'): 12,  # завершення складеного оператора

    # Пробільні символи
    (0, 'ws'): 0,
    (0, 'nl'): 13,

    # Коментарі
    (15, '/'): 17, (17, 'other'): 17, (17, 'nl'): 0,
    (15, 'other'): 12,  # просто ділення

    # Помилки
    (0, 'other'): 101
}

initState = 0  # стартовий стан
F = {2, 6, 9, 10, 11, 12, 13}  # фінальні стани
Fstar = {2, 6, 9}  # стани зі зірочкою (відкат символу)
Ferror = {101, 102}  # стани помилок

tableOfId = {}  # Таблиця ідентифікаторів
tableOfConst = {}  # Таблиця констант
tableOfSymb = {}  # Таблиця символів програми

state = initState
FSuccess = ('Lexer', False)

# Читання тестового файлу
try:
    with open('test.qirim', 'r', encoding='utf-8') as f:
        sourceCode = f.read()
except FileNotFoundError:
    # Якщо файл не знайдено, використовуємо приклад програми
    sourceCode = '''fun main() {
    val x: Int = 10
    var y = x * 2
    val z = x @ 5  // Неочікуваний символ '@'
    val test123x = 5
    val number45abc = 123.45test
    print("Result: $y")
}'''

lenCode = len(sourceCode) - 1
numLine = 1
numChar = -1
char = ''
lexeme = ''


def lex():
    """Основна функція лексичного аналізу"""
    global state, numLine, char, lexeme, numChar, FSuccess
    try:
        while numChar < lenCode:
            char = nextChar()
            classCh = classOfChar(char)
            state = nextState(state, classCh)

            # Перевіряємо на помилку відразу після отримання нового стану
            if state in Ferror:
                # Додаємо проблемний символ до лексеми перед обробкою помилки
                lexeme += char
                fail()
                return  # Зупиняємо аналіз при помилці

            if is_final(state):
                processing()
            elif state == initState:
                lexeme = ''
            else:
                lexeme += char

        # Перевіряємо, чи завершили аналіз у правильному стані
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
    """Обробка фінальних станів"""
    global state, lexeme, char, numLine, numChar, tableOfSymb

    if state == 13:  # новий рядок
        numLine += 1
        state = initState
        return

    if state in (2, 6, 9, 11):  # ідентифікатори, числа, рядки
        # ВИПРАВЛЕНО: Для рядкових констант додаємо останній символ (закриваючу лапку)
        if state == 11:
            lexeme += char

        token = getToken(state, lexeme)
        if token in ('identifier', 'int_const', 'real_const', 'string_const'):
            index = indexIdConst(state, lexeme)
            print('{0:<3d} {1:<15s} {2:<15s} {3:<5}'.format(numLine, lexeme, token, index))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:  # ключові слова, типи або константи
            print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')

        lexeme = ''
        if state in Fstar:
            numChar = putCharBack(numChar)
        state = initState

    if state in (10, 12):  # оператори
        if state == 10:  # складений оператор не завершено
            lexeme += char
        else:  # складений оператор завершено
            lexeme += char

        token = getToken(state, lexeme)
        print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState


def fail():
    """Обробка помилок"""
    global state, numLine, char, lexeme, FSuccess
    FSuccess = ('Lexer', False)

    if state == 101:
        # Виводимо інформацію про проблемний токен
        print(f'{numLine:<3d} {lexeme:<15s} {"UNKNOWN":<15s} {"ERROR":<5s}')

        if char == '@':
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}" (символ @ не підтримується в мові Qirim)')
        elif char in '#$%^&~`':
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}" (символ не підтримується в мові Qirim)')
        elif ord(char) < 32:
            print(f'Лексер: у рядку {numLine} неочікуваний керівний символ (код {ord(char)})')
        else:
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}"')

        # Додаємо проблемний токен до таблиці символів
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, 'UNKNOWN', 'ERROR')

        exit(101)

    if state == 102:
        print(f'Лексер: у рядку {numLine} помилка у складному операторі')
        if lexeme:
            print(f'Лексер: проблематичний оператор: "{lexeme}"')
            # Додаємо проблемний токен до таблиці символів
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, 'UNKNOWN', 'ERROR')
        exit(102)


def is_final(state):
    """Перевірка чи є стан фінальним"""
    return state in F


def nextState(state, classCh):
    """Визначення наступного стану"""
    try:
        return stf[(state, classCh)]
    except KeyError:
        # Якщо точного переходу немає, пробуємо загальний перехід
        if (state, 'other') in stf:
            return stf[(state, 'other')]
        else:
            # Якщо і загального переходу немає, повертаємо помилку
            return 101


def nextChar():
    """Отримання наступного символу"""
    global numChar
    numChar += 1
    if numChar < len(sourceCode):
        return sourceCode[numChar]
    return ''


def putCharBack(numChar):
    """Повернення символу назад"""
    return numChar - 1


def classOfChar(char):
    """Визначення класу символу"""
    if char == '.':
        return "dot"
    elif char.isalpha():
        return "Letter"
    elif char.isdigit():
        return "Digit"
    elif char in " \t\f":
        return "ws"
    elif char in "\n\r":
        return "nl"
    elif char == '_':
        return "_"
    elif char == '$':
        return "$"
    elif char == '"':
        return '"'
    elif char == '`':
        return '`'
    elif char in "+-*/(){},:;?'":
        return char
    elif char in "=!<>&|%":
        return char
    else:
        return 'other'


def getToken(state, lexeme):
    """Отримання типу токену"""
    # Спочатку перевіряємо в таблиці точних збігів
    if lexeme in tokenTable:
        return tokenTable[lexeme]
    # Якщо не знайдено, визначаємо за станом
    if state in tokStateTable:
        return tokStateTable[state]
    return 'unknown'


def indexIdConst(state, lexeme):
    """Отримання індексу ідентифікатора або константи"""
    indx = 0
    if state == 2:  # ідентифікатор
        indx = tableOfId.get(lexeme)
        if indx is None:
            indx = len(tableOfId) + 1
            tableOfId[lexeme] = indx
    if state in (6, 9, 11):  # константи
        indx = tableOfConst.get(lexeme)
        if indx is None:
            indx = len(tableOfConst) + 1
            tableOfConst[lexeme] = (tokStateTable[state], indx)
    return indx


# Запуск лексичного аналізатора
print("=== ЛЕКСИЧНИЙ АНАЛІЗ ПРОГРАМИ НА МОВІ QIRIM ===")
print("Рядок Лексема         Токен           Індекс")
print("-" * 55)

lex()

# Виведення таблиць
if FSuccess[1]:  # Якщо аналіз був успішним
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
        print(f'{value[1]}: {key} ({value[0]})')
else:
    print('\n' + '=' * 60)
    print('АНАЛІЗ ЗАВЕРШЕНО З ПОМИЛКОЮ!')
    print('Таблиці не виводяться через наявність помилок у коді.')
    print('=' * 60)