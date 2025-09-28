# Лексичний аналізатор для мови програмування Qirim (по діаграмі станів)
# Таблиця лексем мови Qirim
tokenTable = {
    # Ключові слова
    'fun':'keyword', 'main':'keyword', 'val':'keyword', 'var':'keyword', 
    'if':'keyword', 'else':'keyword', 'when':'keyword', 'for':'keyword', 
    'do':'keyword', 'while':'keyword', 'return':'keyword', 'continue':'keyword', 
    'break':'keyword', 'is':'keyword', 'in':'keyword', 'downTo':'keyword', 
    'step':'keyword', 'readLine':'keyword', 'print':'keyword',
    
    # Типи даних
    'Int':'type', 'Real':'type', 'String':'type', 'Boolean':'type', 'Unit':'type',
    
    # Логічні константи
    'true':'bool_const', 'false':'bool_const',
    
    # Оператори
    '=':'assign_op', 
    '+':'add_op', '-':'add_op', 
    '*':'mult_op', '/':'mult_op', '%':'mult_op',
    '**':'exp_op',
    '==':'rel_op', '!=':'rel_op', '<':'rel_op', '>':'rel_op', 
    '<=':'rel_op', '>=':'rel_op',
    '&&':'logical_op', '||':'logical_op', '!':'logical_op',
    
    # Роздільники і дужки
    '(':'brackets_op', ')':'brackets_op', '{':'brackets_op', '}':'brackets_op',
    '.':'punct', ',':'punct', ':':'punct', ';':'punct', '?':'punct', 
    "'":"punct", '"':'punct', '`':'punct', '->':'punct', '..':'punct',
}

# Токени за станами 
tokStateTable = {
    2:'identifier',    # Стан 2 - ідентифікатори
    5:'real_const',    # Стан 5 - дійсні числа  
    6:'int_const',     # Стан 6 - цілі числа
    12:'string_const'  # Стан 12 - рядкові константи
}

# Діаграма станів - строго по диаграмме
stf = {
    # З стану 0 (початковий)
    (0, 'Letter'): 1,    # Літери -> стан 1
    (0, 'Digit'): 3,     # Цифри -> стан 3
    (0, '"'): 10,        # Лапки -> стан 10 (початок рядка)
    (0, 'ws'): 0,        # Пробіли залишаються в стані 0
    (0, 'nl'): 0,        # Новий рядок теж залишається в стані 0
    (0, '.'): 4,         # Крапка -> стан 4
    
    # Стан 1 - читання ідентифікатора
    (1, 'Letter'): 1,    # Літери залишаються в стані 1
    (1, 'Digit'): 1,     # Цифри залишаються в стані 1
    (1, 'other'): 2,     # Інше -> стан 2 (кінець ідентифікатора)
    
    # Стан 3 - читання цілого числа
    (3, 'Digit'): 3,     # Цифри залишаються в стані 3
    (3, '.'): 4,         # Крапка -> стан 4 (початок дробової частини)
    (3, 'Letter'): 101,  # Літера після цифри -> ПОМИЛКА!
    (3, 'other'): 6,     # Інше -> стан 6 (кінець цілого числа)
    
    # Стан 4 - після крапки
    (4, 'Digit'): 4,     # Цифри залишаються в стані 4
    (4, 'other'): 5,     # Інше -> стан 5 (кінець дійсного числа)
    
    # Стан 10 - початок рядка  
    (10, '"'): 12,       # Закриваюча лапка -> стан 12 (кінець рядка)
    (10, 'other'): 11,   # Інше -> стан 11 (читання рядка)
    (10, 'nl'): 11,      # Новий рядок -> стан 11
    (10, 'ws'): 11,      # Пробіли -> стан 11
    
    # Стан 11 - читання рядка
    (11, '"'): 12,       # Закриваюча лапка -> стан 12
    (11, 'other'): 11,   # Інше залишається в стані 11
    (11, 'nl'): 11,      # Новий рядок залишається в стані 11
    (11, 'ws'): 11,      # Пробіли залишаються в стані 11
    
    # Загальний перехід для помилок
    (0, 'other'): 101,
}

# Одиночные операторы сразу распознаются
single_char_tokens = {
    '+': 'add_op', '-': 'add_op',
    '*': 'mult_op', '/': 'mult_op', '%': 'mult_op',
    '(': 'brackets_op', ')': 'brackets_op', '{': 'brackets_op', '}': 'brackets_op',
    ',': 'punct', ':': 'punct', ';': 'punct', '?': 'punct', "'": 'punct',
    '=': 'assign_op', '!': 'logical_op', '<': 'rel_op', '>': 'rel_op',
    '&': 'logical_op', '|': 'logical_op'
}

initState = 0   # стартовый стан
F = {2, 5, 6, 12, 101}  # фінальні стани СТРОГО по диаграмме
Fstar = {2, 5, 6}       # стани зі зірочкою (відкат символу)
Ferror = {101}          # стани помилок

tableOfId = {}     # Таблиця ідентифікаторів
tableOfConst = {}  # Таблиця констант
tableOfSymb = {}   # Таблиця символів програми

state = initState
FSuccess = ('Lexer', False)

# Читаем существующий файл test.qirim
with open('test.qirim', 'r', encoding='utf-8') as file:
    sourceCode = file.read()

lenCode = len(sourceCode)
numLine = 1
numChar = -1
char = ''
lexeme = ''

def lex():
    """Основна функція лексичного аналізу"""
    global state, numLine, char, lexeme, numChar, FSuccess
    try:
        while numChar < lenCode - 1:
            char = nextChar()
            classCh = classOfChar(char)
            
            # Обробляємо новий рядок окремо
            if classCh == 'nl':
                numLine += 1
                continue
                
            # Пропускаємо пробіли, коли не в рядку
            if classCh == 'ws' and state == 0:
                continue
            
            # Специальная обработка одиночных операторов
            if state == 0 and char in single_char_tokens:
                lexeme = char
                token = single_char_tokens[char]
                print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
                tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
                lexeme = ''
                continue
                
            state = nextState(state, classCh)
            
            # Перевіряємо на помилку
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
                
        # Перевіряємо завершення
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
        
    if state in (2, 5, 6, 12):  # кінцеві стани токенів
        # Для рядкових констант додаємо закриваючу лапку
        if state == 12:
            lexeme += char
            
        token = getToken(state, lexeme)
        if token in ('identifier', 'int_const', 'real_const', 'string_const'):
            index = indexIdConst(state, lexeme)
            print('{0:<3d} {1:<15s} {2:<15s} {3:<5}'.format(numLine, lexeme, token, index))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:  # ключові слова, типи
            print('{0:<3d} {1:<15s} {2:<15s}'.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        
        lexeme = ''
        if state in Fstar:
            numChar = putCharBack(numChar)
        state = initState

def fail():
    """Обробка помилок"""
    global state, numLine, char, lexeme, FSuccess
    FSuccess = ('Lexer', False)
    
    if state == 101:
        print(f'{numLine:<3d} {lexeme:<15s} {"UNKNOWN":<15s} {"ERROR":<5s}')
        
        # Специальная обработка для чисел с буквами
        if lexeme and lexeme[0].isdigit() and any(c.isalpha() for c in lexeme):
            print(f'Лексер: у рядку {numLine} ідентифікатор не може починатися з цифр')
        elif is_cyrillic(char):
            print(f'Лексер: у рядку {numLine} неочікуваний символ кирилиці "{char}" (підтримуються лише латинські літери)')
        elif char == '@':
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}" (символ @ не підтримується)')
        elif char in '#$%^&~':
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}" (символ не підтримується)')
        else:
            print(f'Лексер: у рядку {numLine} неочікуваний символ "{char}"')
        
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, 'UNKNOWN', 'ERROR')
        exit(101)

def is_cyrillic(char):
    """Перевірка чи є символ кирилицею"""
    return '\u0400' <= char <= '\u04FF' or '\u0500' <= char <= '\u052F'

def is_final(state):
    """Перевірка чи є стан фінальним"""
    return state in F

def nextState(state, classCh):
    """Визначення наступного стану"""
    try:
        return stf[(state, classCh)]
    except KeyError:
        # Пробуємо загальний перехід
        if (state, 'other') in stf:
            return stf[(state, 'other')]
        else:
            return 101  # помилка

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
        return "."
    elif char.isalpha() and not is_cyrillic(char):  # Тільки латинські літери
        return "Letter"
    elif is_cyrillic(char):  # Кирилиця - помилка
        return "other"
    elif char.isdigit():
        return "Digit"
    elif char in " \t\f":
        return "ws"
    elif char in "\n\r":
        return "nl"
    elif char == '"':
        return '"'
    elif char in "+-*/(){},:;?'=!<>&|%":
        return char
    else:
        return 'other'

def getToken(state, lexeme):
    """Отримання типу токену"""
    # Спочатку перевіряємо точні збіги
    if lexeme in tokenTable:
        return tokenTable[lexeme]
    # Потім за станом
    if state in tokStateTable:
        return tokStateTable[state]
    return 'unknown'

def indexIdConst(state, lexeme):
    """ПРАВИЛЬНАЯ функция индексации"""
    if state == 2:  # ідентифікатор - состояние 2
        if lexeme not in tableOfId:
            tableOfId[lexeme] = len(tableOfId) + 1
        return tableOfId[lexeme]
    
    elif state in (5, 6, 12):  # константи - состояния 5, 6, 12
        if lexeme not in tableOfConst:
            tableOfConst[lexeme] = len(tableOfConst) + 1
        return tableOfConst[lexeme]
    
    return 0

# Запуск аналізатора
print("=== ЛЕКСИЧНИЙ АНАЛІЗ ПРОГРАМИ НА МОВІ QIRIM ===")
print("=== ПО ДІАГРАМІ СТАНІВ ===")
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