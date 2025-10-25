from prettytable import PrettyTable
import lex_qirim

lex_qirim.lex()

tableOfSymb = lex_qirim.tableOfSymb
tableOfId = lex_qirim.tableOfId
tableOfConst = lex_qirim.tableOfConst
statusMessage = lex_qirim.statusMessage
FSuccess = lex_qirim.FSuccess

len_tableOfSymb = len(tableOfSymb)

numRow = 1
stepIdent = 2
ident = 0

# Таблиця змінних: {identifier: {'type': type, 'initialized': bool, 'mutable': bool, 'line': numLine}}
tableOfVar = {}

# Таблиця функцій: {func_name: {'params': [(name, type, has_default)], 'return_type': type, 'line': numLine}}
tableOfFunc = {}

# Контекст поточної функції
currentFunction = None

TRACE = False


def trace(msg):
    if TRACE:
        print(msg)


def next_ident():
    global ident
    ident += stepIdent
    return " " * ident


def prev_ident():
    global ident
    ident -= stepIdent
    return " " * ident


def get_symb():
    if numRow > len_tableOfSymb:
        fail_parse("неочікуваний кінець програми", numRow)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


def fail_parse(msg, data):
    if msg == "неочікуваний кінець програми":
        row = data
        print("\nParser ERROR:")
        print(f"НЕОЧІКУВАНИЙ КІНЕЦЬ ПРОГРАМИ! У таблиці символів немає запису з номером {row}.")
        if row > 1:
            print(f"ОСТАННІЙ ЗАПИС У ТАБЛИЦІ: {tableOfSymb[row - 1]}")
        exit(1002)
    elif msg == "несумісність токенів":
        numLine, lexeme, token, expected_lex, expected_tok = data
        print("\nParser ERROR:")
        print(f"У рядку {numLine} знайдено НЕСПОДІВАНИЙ елемент: {lexeme}, {token}")
        print(f"ОЧІКУВАВСЯ: {expected_lex}, {expected_tok}")
        exit(1003)
    elif msg == "невідповідність у PrimaryExpr":
        numLine, lexeme, token, expected = data
        print("\nParser ERROR:")
        print(f"У рядку {numLine} знайдено {lexeme}, {token}, а очікувалося - {expected}")
        exit(1004)
    elif msg == "Незакритий оператор when":
        print("\nParser ERROR: Відсутня закриваюча фігурна дужка } для when")
        exit(1005)
    elif msg == "readLine() має бути без параметрів":
        numLine, lexeme, token, expected_lex, expected_tok = data
        print("\nParser ERROR:")
        print(f"У рядку {numLine} знайдено {lexeme}, {token}, а очікувалося - {expected_lex}, {expected_tok}")
        exit(1006)
    elif msg == "Незакритий блок { ... }":
        print("\nParser ERROR: Відсутня закриваюча фігурна дужка } для блоку")
        exit(1007)
    else:
        print(f"\nParser ERROR: {msg}")
        print(f"Дані: {data}")
        exit(1004)


def fail_semantic(msg, data):
    """Обробка семантичних помилок"""
    print("\nSEMANTIC ERROR:")
    if msg == "повторне оголошення змінної":
        numLine, var_name, first_line = data
        print(f"У рядку {numLine}: Змінна '{var_name}' вже була оголошена у рядку {first_line}")
        exit(2001)
    elif msg == "повторне оголошення функції":
        numLine, func_name, first_line = data
        print(f"У рядку {numLine}: Функція '{func_name}' вже була оголошена у рядку {first_line}")
        exit(2002)
    elif msg == "використання неоголошеної змінної":
        numLine, var_name = data
        print(f"У рядку {numLine}: Змінна '{var_name}' не була оголошена")
        exit(2003)
    elif msg == "використання неініціалізованої змінної":
        numLine, var_name = data
        print(f"У рядку {numLine}: Змінна '{var_name}' не була ініціалізована")
        exit(2004)
    elif msg == "несумісність типів у присвоєнні":
        numLine, var_name, var_type, expr_type = data
        print(f"У рядку {numLine}: Несумісність типів при присвоєнні змінній '{var_name}'")
        print(f"Тип змінної: {var_type}, тип виразу: {expr_type}")
        exit(2005)
    elif msg == "присвоєння val змінній":
        numLine, var_name = data
        print(f"У рядку {numLine}: Неможливо змінити значення val змінної '{var_name}'")
        exit(2006)
    elif msg == "несумісність типів операндів":
        numLine, op, left_type, right_type = data
        print(f"У рядку {numLine}: Несумісні типи операндів для оператора '{op}'")
        print(f"Лівий операнд: {left_type}, правий операнд: {right_type}")
        exit(2007)
    elif msg == "невідомий тип":
        numLine, type_name = data
        print(f"У рядку {numLine}: Невідомий тип '{type_name}'")
        exit(2008)
    elif msg == "використання неоголошеної функції":
        numLine, func_name = data
        print(f"У рядку {numLine}: Функція '{func_name}' не була оголошена")
        exit(2009)
    elif msg == "невідповідність кількості параметрів":
        numLine, func_name, expected, actual = data
        print(f"У рядку {numLine}: Невірна кількість параметрів при виклику функції '{func_name}'")
        print(f"Очікувалось: {expected}, отримано: {actual}")
        exit(2010)
    elif msg == "невідповідність типів параметрів":
        numLine, func_name, param_num, expected_type, actual_type = data
        print(f"У рядку {numLine}: Невідповідність типу параметра #{param_num} у виклику '{func_name}'")
        print(f"Очікувався тип: {expected_type}, отримано: {actual_type}")
        exit(2011)
    elif msg == "відсутній return у функції":
        numLine, func_name, return_type = data
        print(f"У рядку {numLine}: Функція '{func_name}' має тип повернення '{return_type}', але відсутній return")
        exit(2012)
    elif msg == "невідповідність типу return":
        numLine, func_name, expected_type, actual_type = data
        print(f"У рядку {numLine}: Невідповідність типу return у функції '{func_name}'")
        print(f"Очікувався тип: {expected_type}, отримано: {actual_type}")
        exit(2013)
    else:
        print(f"ПОМИЛКА: {msg}")
        print(f"Дані: {data}")
        exit(2099)


def get_type_const(lexeme):
    """Отримати тип константи з таблиці констант"""
    if lexeme in tableOfConst:
        _, numLine, lex, tok, _ = tableOfSymb[tableOfConst[lexeme]]
        if tok == 'int_const':
            return 'Int'
        elif tok == 'real_const':
            return 'Real'
        elif tok == 'string_const':
            return 'String'
        elif tok == 'bool_const':
            return 'Boolean'
    return None


def get_type_var(var_name):
    """Отримати тип змінної"""
    if var_name in tableOfVar:
        return tableOfVar[var_name]['type']
    return None


def is_var_initialized(var_name):
    """Перевірити, чи змінна ініціалізована"""
    if var_name in tableOfVar:
        return tableOfVar[var_name]['initialized']
    return False


def is_var_mutable(var_name):
    """Перевірити, чи змінна може бути змінена (var vs val)"""
    if var_name in tableOfVar:
        return tableOfVar[var_name]['mutable']
    return False


def add_var_to_table(var_name, var_type, is_mutable, is_initialized, numLine):
    """Додати змінну до таблиці змінних"""
    if var_name in tableOfVar:
        fail_semantic("повторне оголошення змінної", (numLine, var_name, tableOfVar[var_name]['line']))
    tableOfVar[var_name] = {
        'type': var_type,
        'initialized': is_initialized,
        'mutable': is_mutable,
        'line': numLine
    }
    print(f"    [Semantic] Додано змінну: {var_name}, тип: {var_type}, mutable: {is_mutable}, line: {numLine}")


def set_var_initialized(var_name):
    """Позначити змінну як ініціалізовану"""
    if var_name in tableOfVar:
        tableOfVar[var_name]['initialized'] = True


def add_func_to_table(func_name, params, return_type, numLine):
    """Додати функцію до таблиці функцій"""
    if func_name in tableOfFunc:
        fail_semantic("повторне оголошення функції", (numLine, func_name, tableOfFunc[func_name]['line']))
    tableOfFunc[func_name] = {
        'params': params,
        'return_type': return_type,
        'line': numLine
    }
    print(f"    [Semantic] Додано функцію: {func_name}, params: {params}, return_type: {return_type}, line: {numLine}")


def get_type_op(left_type, op, right_type):
    """Визначити тип результату операції"""
    # Арифметичні оператори
    if op in ('+', '-', '*', '/', '%', '**'):
        if left_type in ('Int', 'Real') and right_type in ('Int', 'Real'):
            if left_type == 'Real' or right_type == 'Real':
                return 'Real'
            return 'Int'
        return 'type_error'
    
    # Оператори порівняння
    if op in ('==', '!=', '<', '<=', '>', '>='):
        if left_type == right_type and left_type in ('Int', 'Real', 'Boolean'):
            return 'Boolean'
        if left_type in ('Int', 'Real') and right_type in ('Int', 'Real'):
            return 'Boolean'
        return 'type_error'
    
    # Логічні оператори
    if op in ('&&', '||'):
        if left_type == 'Boolean' and right_type == 'Boolean':
            return 'Boolean'
        return 'type_error'
    
    return 'type_error'


def parse_token(lexeme, token):
    global numRow
    indent = next_ident()
    if numRow > len_tableOfSymb:
        fail_parse("неочікуваний кінець програми", (lexeme, token, numRow))
    numLine, lex, tok = get_symb()
    numRow += 1

    print(f"{indent}parse_token(): Рядок {numLine} - токен {lex}, {tok}")
    trace(f"{indent}очікувалося: {lexeme}, {token}")

    if (lex, tok) == (lexeme, token):
        res = True
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, lexeme, token))
        res = False

    prev_ident()
    return res


def parse_program():
    try:
        indent = next_ident()
        print(f"{indent}parse_program():")
        found_main = False
        while numRow <= len_tableOfSymb:
            numLine, lex, tok = get_symb()
            if lex == "fun" and tok == "keyword":
                if numRow + 1 <= len_tableOfSymb:
                    _, next_lex, next_tok, _ = tableOfSymb[numRow + 1]
                    if next_lex == "main" and next_tok == "keyword":
                        found_main = True
                        break
                parse_function_declaration()
            else:
                break
        if not found_main:
            print("\nАВАРІЙНЕ ЗАВЕРШЕННЯ ПРОГРАМИ! У даній програмі немає точки входу fun main() {...}.")
            exit(2001)
        parse_main_function()
        while numRow <= len_tableOfSymb:
            numLine, lex, tok = get_symb()
            if lex == "fun" and tok == "keyword":
                parse_function_declaration()
            else:
                break
        if numRow == len_tableOfSymb + 1:
            print("\nСинтаксичний аналіз завершився успішно!")
            print("\nСЕМАНТИЧНИЙ АНАЛІЗ ЗАВЕРШИВСЯ УСПІШНО!")
            return True
        else:
            print("\nПОМИЛКА! Очікується оголошення ВЕРХНЬОГО рівня.")
            return False
    except SystemExit as e:
        print(f"КОД ПОМИЛКИ: {e}")
        return False
    finally:
        prev_ident()


def parse_main_function():
    global numRow, currentFunction
    indent = next_ident()
    print(f"{indent}parse_main_function():")
    currentFunction = 'main'

    start_line, _, _ = get_symb()

    parse_token("fun", "keyword")
    parse_token("main", "keyword")
    parse_token("(", "brackets_op")
    parse_token(")", "brackets_op")
    add_func_to_table('main', [], 'Unit', start_line)
    parse_block(is_function_block=True, function_name="main")
    currentFunction = None
    prev_ident()
    return True


def parse_function_declaration():
    global numRow, currentFunction
    indent = next_ident()
    print(f"{indent}parse_function_declaration():")
    parse_token("fun", "keyword")
    numLine, lex, tok = get_symb()
    if tok == "identifier":
        print(f"{indent}Ім'я функції: {lex}")
        function_name = lex
        func_line = numLine
        currentFunction = function_name
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))

    parse_token("(", "brackets_op")
    params = []
    numLine, lex, tok = get_symb()
    if lex != ")":
        params = parse_params()
    parse_token(")", "brackets_op")

    return_type = 'Unit'
    numLine, lex, tok = get_symb()
    if lex == ":" and tok == "punct":
        numRow += 1
        return_type = parse_return_type()

    add_func_to_table(function_name, params, return_type, func_line)

    for param_name, param_type, has_default in params:
        if param_name not in tableOfVar:  # Проста перевірка, щоб уникнути конфліктів
            add_var_to_table(param_name, param_type, is_mutable=False, is_initialized=True, numLine=func_line)


    numLine, lex, tok = get_symb()
    if lex == "=" and tok == "assign_op":
        numRow += 1
        expr_type = parse_expression()
        if return_type != 'Unit' and expr_type != return_type:
            # Дозволяємо неявне перетворення Int -> Real
            if not (return_type == 'Real' and expr_type == 'Int'):
                fail_semantic("невідповідність типу return", (numLine, function_name, return_type, expr_type))
    elif lex == "{" and tok == "brackets_op":
        parse_block(is_function_block=True, function_name=function_name)
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "= або {", "(assign_op або brackets_op)"))


    for param_name, _, _ in params:
        if param_name in tableOfVar and tableOfVar[param_name]['line'] == func_line:
            del tableOfVar[param_name]
            print(f"    [Semantic] Видалено параметр: {param_name} з tableOfVar")

    currentFunction = None
    prev_ident()
    return True


def parse_params():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_params():")
    params = []
    param = parse_param()
    params.append(param)
    while True:
        numLine, lex, tok = get_symb()
        if lex == "," and tok == "punct":
            numRow += 1
            param = parse_param()
            params.append(param)
        else:
            break
    prev_ident()
    return params


def parse_param():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_param():")
    numLine, lex, tok = get_symb()
    param_name = None
    if tok == "identifier":
        print(f"{indent}Параметр: {lex}")
        param_name = lex
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    
    parse_token(":", "punct")
    param_type = parse_type()
    
    has_default = False
    numLine, lex, tok = get_symb()
    if lex == "=" and tok == "assign_op":
        numRow += 1
        default_type = parse_expression()
        if default_type != param_type:
            fail_semantic("несумісність типів у присвоєнні", (numLine, param_name, param_type, default_type))
        has_default = True
    
    prev_ident()
    return (param_name, param_type, has_default)


def parse_type():
    global numRow
    indent = next_ident()
    numLine, lex, tok = get_symb()
    if tok == "type" or (lex == "Unit" and tok == "keyword"):
        print(f"{indent}Тип: {lex}")
        numRow += 1
        prev_ident()
        return lex
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "type", "type"))


def parse_return_type():
    global numRow
    indent = next_ident()
    numLine, lex, tok = get_symb()
    if tok == "type" or (lex == "Unit" and tok == "keyword"):
        print(f"{indent}Тип повернення: {lex}")
        numRow += 1
        prev_ident()
        return lex
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "type або Unit", "type"))


def parse_block(is_function_block=False, function_name=None):
    global numRow
    indent = next_ident()
    print(f"{indent}parse_block():")

    start_line, _, _ = get_symb()
    parse_token("{", "brackets_op")

    has_return_statement = False
    last_line_before_brace = start_line

    while True:
        if numRow > len_tableOfSymb:
            if is_function_block:
                print(
                    f"Parser ERROR: Незакрита функція {function_name if function_name else ""} (блок почався у рядку {start_line})")
                exit(1010)
            else:
                print(f"ПОМИЛКА! Очікувався: '}}'. Блок почався у рядку {start_line}.")
                exit(1009)

        current_line, _, _ = get_symb()
        if current_line > last_line_before_brace:
            last_line_before_brace = current_line

        statement_type = parse_function_statement(is_function_block, function_name)

        if statement_type == 'return':
            has_return_statement = True
        elif statement_type == 'end_of_block':
            break

    if is_function_block and function_name and function_name in tableOfFunc:
        expected_type = tableOfFunc[function_name]['return_type']
        if expected_type != 'Unit' and not has_return_statement:
            fail_semantic("відсутній return у функції", (last_line_before_brace, function_name, expected_type))

    parse_token("}", "brackets_op")
    prev_ident()
    return True


def parse_function_statement(is_function_block=False, function_name=None):
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_function_statement():")
    if numRow > len_tableOfSymb:
        if is_function_block:
            print(f"Parser ERROR: Незакрита функція {function_name if function_name else ""}")
            exit(1010)
        else:
            print("ПОМИЛКА! Очікувався: '}'.")
            exit(1009)

    numLine, lex, tok = get_symb()

    if is_function_block and lex == "fun" and tok == "keyword":
        print(
            f"Parser ERROR: Вкладене оголошення функції у тілі функції '{function_name if function_name else ''}' не дозволено.")
        exit(1011)

    if lex == "}" and tok == "brackets_op":
        prev_ident()
        return 'end_of_block'

    result = 'other_statement'
    if lex in ("val", "var") and tok == "keyword":
        parse_variable_declarations()
        result = 'variable_declaration'
    elif lex == "return" and tok == "keyword":
        result = parse_return_statement()
    else:
        parse_statement_section(is_function_block, function_name)

    prev_ident()
    return result


def parse_variable_declarations():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_variable_declarations():")
    first_decl_line, _, _ = get_symb()
    parse_variable_declaration()
    while True:
        numLine, lex, tok = get_symb()
        if lex == ";" and tok == "punct":
            numRow += 1
            numLine, lex, tok = get_symb()
            if lex in ("val", "var") and tok == "keyword":
                if numLine == first_decl_line:
                    parse_variable_declaration()
                else:
                    numRow -= 1
                    break
            else:
                break
        else:
            if lex in ("val", "var") and tok == "keyword" and numLine == first_decl_line:
                fail_parse("несумісність токенів",
                           (numLine, lex, tok, ";", "punct - між оголошеннями в одному рядку потрібна крапка з комою"))
            break
    prev_ident()
    return True


def parse_variable_declaration():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_variable_declaration():")
    numLine, lex, tok = get_symb()
    is_mutable = False
    if lex in ("var", "val") and tok == "keyword":
        print(f"{indent}Тип оголошення: {lex}")
        is_mutable = (lex == "var")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "var або val", "keyword"))
    parse_declaration(is_mutable)
    prev_ident()
    return True


def parse_declaration(is_mutable):
    global numRow
    indent = next_ident()
    print(f"{indent}parse_declaration():")
    numLine, lex, tok = get_symb()
    var_name = None
    if tok == "identifier":
        print(f"{indent}Змінна: {lex}")
        var_name = lex
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, 'identifier', 'identifier'))
    
    numLine, lex, tok = get_symb()
    var_type = None
    is_initialized = False
    
    if lex == ":" and tok == "punct":
        numRow += 1
        var_type = parse_type()
        numLine, lex, tok = get_symb()
        if lex == "=" and tok == "assign_op":
            numRow += 1
            expr_type = parse_expression()
            if var_type != expr_type:
                if not (var_type == 'Real' and expr_type == 'Int'):
                    fail_semantic("несумісність типів у присвоєнні", (numLine, var_name, var_type, expr_type))
            is_initialized = True
    elif lex == "=" and tok == "assign_op":
        numRow += 1
        var_type = parse_expression()
        is_initialized = True
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "var/val, : або =", 'punct або assign_op'))
    
    add_var_to_table(var_name, var_type, is_mutable, is_initialized, numLine)
    prev_ident()
    return True


def parse_statement_section(is_function_block=False, function_name=None):
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_statement_section():")
    while True:
        if numRow > len_tableOfSymb:
            if is_function_block:
                print(f"Parser ERROR: Незакрита функція {function_name if function_name else ''}")
                exit(1010)
            else:
                print("ПОМИЛКА! Очікувався: '}'.")
                exit(1009)
        numLine, lex, tok = get_symb()
        if lex == "}" and tok == "brackets_op":
            break
        if lex == ";" and tok == "punct":
            numRow += 1
            continue
        if not parse_statement(is_function_block, function_name):
            break
    prev_ident()
    return True


def parse_statement(is_function_block=False, function_name=None):
    global numRow
    indent = next_ident()
    print(f"{indent}parse_statement():")
    if numRow > len_tableOfSymb:
        if is_function_block:
            print(f"Parser ERROR: Незакрита функція {function_name if function_name else ''}")
            exit(1010)
        else:
            print("ПОМИЛКА! Очікувався: '}'.")
            exit(1009)
    numLine, lex, tok = get_symb()

    if lex == "}" and tok == "brackets_op":
        prev_ident()
        return False
    if lex == "print" and tok == "keyword":
        parse_output_statement()
    elif lex == "for" and tok == "keyword":
        parse_for_statement()
    elif lex == "while" and tok == "keyword":
        parse_while_statement()
    elif lex == "do" and tok == "keyword":
        parse_do_while_statement()
    elif lex == "if" and tok == "keyword":
        parse_if_statement()
    elif lex == "when" and tok == "keyword":
        parse_when_statement()
    elif tok == "identifier":
        if numRow + 1 <= len_tableOfSymb:
            _, next_lex, next_tok, _ = tableOfSymb[numRow + 1]
            if next_lex == '=' and next_tok == 'assign_op':
                if numRow + 2 <= len_tableOfSymb:
                    _, after_eq_lex, after_eq_tok, _ = tableOfSymb[numRow + 2]
                    if after_eq_lex == "readLine" and after_eq_tok == "keyword":
                        parse_input_statement()
                    else:
                        parse_assignment_statement()
                else:
                    parse_assignment_statement()
            elif next_lex == "(" and next_tok == "brackets_op":
                parse_function_call_statement()
            else:
                fail_parse("несумісність токенів",
                           (numLine, lex, tok, "val, var, = або (", "keyword, assign_op або brackets_op"))
        else:
            fail_parse("неочікуваний кінець програми", numRow)
    else:
        if tok == 'keyword' and lex in ('var', 'val'):
            parse_variable_declarations()
            prev_ident()
            return True
        else:
            print(f"Parser ERROR: Неочікуваний токен '{lex}' типу '{tok}' в рядку {numLine}.")
            exit(1014)
        prev_ident()
        return False
    prev_ident()
    return True


def parse_assignment_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_assignment_statement():")
    numLine, lex, tok = get_symb()
    var_name = None
    if tok == "identifier":
        print(f"{indent}Змінна: {lex}")
        var_name = lex
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    
    # Семантичні перевірки
    if var_name not in tableOfVar:
        fail_semantic("використання неоголошеної змінної", (numLine, var_name))
    
    if not is_var_mutable(var_name):
        fail_semantic("присвоєння val змінній", (numLine, var_name))
    
    var_type = get_type_var(var_name)
    
    parse_token("=", "assign_op")
    expr_type = parse_expression()
    
    if var_type != expr_type:
        if not (var_type == 'Real' and expr_type == 'Int'):
            fail_semantic("несумісність типів у присвоєнні", (numLine, var_name, var_type, expr_type))
    
    set_var_initialized(var_name)
    
    prev_ident()
    return True


def parse_input_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_input_statement():")
    numLine, lex, tok = get_symb()
    var_name = None
    if tok == "identifier":
        print(f"{indent}Змінна вводу: {lex}")
        var_name = lex
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    
    # Семантичні перевірки
    if var_name not in tableOfVar:
        fail_semantic("використання неоголошеної змінної", (numLine, var_name))
    
    var_type = get_type_var(var_name)
    if var_type != 'String':
        print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: readLine() повертає String, а змінна '{var_name}' має тип {var_type}")
    
    parse_token("=", "assign_op")
    parse_token("readLine", "keyword")
    parse_token("(", "brackets_op")
    parse_token(")", "brackets_op")
    
    set_var_initialized(var_name)
    
    prev_ident()
    return True


def parse_output_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_output_statement():")
    parse_token("print", "keyword")
    parse_token("(", "brackets_op")
    numLine, lex, tok = get_symb()
    if lex != ")" or tok != "brackets_op":
        if tok == "string_const" and ("${" in lex):
            numRow += 1
        else:
            parse_expression()
    parse_token(")", "brackets_op")
    prev_ident()
    return True


def parse_function_call_statement():
    indent = next_ident()
    print(f"{indent}parse_function_call_statement():")
    parse_function_call()
    prev_ident()
    return True


def parse_for_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_for_statement():")
    parse_token("for", "keyword")
    parse_token("(", "brackets_op")
    numLine, lex, tok = get_symb()
    var_name = None
    if tok == "identifier":
        print(f"{indent}Змінна циклу: {lex}")
        var_name = lex
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    
    # Семантична перевірка
    if var_name not in tableOfVar:
        fail_semantic("використання неоголошеної змінної", (numLine, var_name))
    
    var_type = get_type_var(var_name)
    if var_type != 'Int':
        print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Змінна циклу '{var_name}' має тип {var_type}, очікувався Int")
    
    parse_token("in", "keyword")
    parse_for_range()
    parse_token(")", "brackets_op")
    parse_do_block()
    prev_ident()
    return True


def parse_for_range():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_for_range():")
    range_start_type = parse_expression()
    numLine, lex, tok = get_symb()
    
    if lex == ".." and tok == "punct":
        numRow += 1
        range_end_type = parse_expression()
        if range_start_type != 'Int' or range_end_type != 'Int':
            print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Діапазон має бути Int..Int, отримано {range_start_type}..{range_end_type}")
        numLine, lex, tok = get_symb()
    elif lex == "downTo" and tok == "keyword":
        numRow += 1
        range_end_type = parse_expression()
        if range_start_type != 'Int' or range_end_type != 'Int':
            print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Діапазон має бути Int downTo Int, отримано {range_start_type} downTo {range_end_type}")
        numLine, lex, tok = get_symb()
    
    if lex == "step" and tok == "keyword":
        numRow += 1
        parse_step_expr()
    elif lex not in (")", "step"):
        fail_parse("несумісність токенів",
                   (numLine, lex, tok, ".., downTo, step або )", "punct, keyword або brackets_op"))
    prev_ident()
    return True


def parse_step_expr():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_step_expr():")
    numLine, lex, tok = get_symb()
    if tok == "int_const":
        numRow += 1
        print(f"{indent}Крок циклу: {lex}")
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "int_const", "int_const"))
    prev_ident()
    return True


def parse_do_block(is_function_block=False, function_name=None):
    global numRow
    indent = next_ident()
    print(f"{indent}parse_do_block():")
    numLine, lex, tok = get_symb()
    if lex == "{" and tok == "brackets_op":
        numRow += 1
        parse_statement_section(is_function_block, function_name)
        if numRow > len_tableOfSymb:
            fail_parse("Незакритий блок { ... }", (numLine, lex, tok))
        numLine2, lex2, tok2 = get_symb()
        if lex2 == "}" and tok2 == 'brackets_op':
            parse_token("}", "brackets_op")
        else:
            fail_parse("Незакритий блок { ... }", (numLine2, lex2, tok2))
    else:
        parse_statement(is_function_block, function_name)
    prev_ident()
    return True


def parse_while_statement():
    indent = next_ident()
    print(f"{indent}parse_while_statement():")
    parse_token("while", "keyword")
    parse_token("(", "brackets_op")
    cond_type = parse_expression()
    if cond_type != 'Boolean':
        print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Умова while має бути Boolean, отримано {cond_type}")
    parse_token(")", "brackets_op")
    parse_do_block()
    prev_ident()
    return True


def parse_do_while_statement():
    indent = next_ident()
    print(f"{indent}parse_do_while_statement():")
    parse_token("do", "keyword")
    parse_do_block()
    parse_token("while", "keyword")
    parse_token("(", "brackets_op")
    cond_type = parse_expression()
    if cond_type != 'Boolean':
        print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Умова do-while має бути Boolean, отримано {cond_type}")
    parse_token(")", "brackets_op")
    prev_ident()
    return True


def parse_if_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_if_statement():")

    parse_token("if", "keyword")
    parse_token("(", "brackets_op")
    cond_type = parse_expression()
    if cond_type != 'Boolean':
        print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Умова if має бути Boolean, отримано {cond_type}")
    parse_token(")", "brackets_op")
    parse_do_block()
    numLine, lex, tok = get_symb()
    if lex == "else" and tok == "keyword":
        numRow += 1
        parse_do_block()
    prev_ident()
    return True


def parse_when_statement():
    indent = next_ident()
    print(f"{indent}parse_when_statement():")
    parse_token("when", "keyword")
    parse_token("(", "brackets_op")
    when_expr_type = parse_expression()
    parse_token(")", "brackets_op")
    parse_token("{", "brackets_op")
    parse_when_entry(when_expr_type)
    while True:
        if numRow > len_tableOfSymb:
            fail_parse("Незакритий оператор when", (None, None, None))
        numLine, lex, tok = get_symb()
        if lex == "}" and tok == "brackets_op":
            break
        parse_when_entry(when_expr_type)
    parse_token("}", "brackets_op")
    prev_ident()
    return True


def parse_when_entry(when_expr_type):
    indent = next_ident()
    print(f"{indent}parse_when_entry():")
    parse_when_condition(when_expr_type)
    parse_token('->', 'punct')
    parse_do_block()
    prev_ident()
    return True


def parse_when_condition(when_expr_type):
    global numRow
    indent = next_ident()
    print(f"{indent}parse_when_condition():")

    _, lex, tok = get_symb()
    if lex == "else" and tok == "keyword":
        numRow += 1
        prev_ident()
        return

    cond_type = parse_expression()
    if cond_type != when_expr_type:
        print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Тип умови when ({cond_type}) не співпадає з типом виразу ({when_expr_type})")
    
    while True:
        _, lex, tok = get_symb()
        if lex == "," and tok == "punct":
            numRow += 1
            cond_type = parse_expression()
            if cond_type != when_expr_type:
                print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Тип умови when ({cond_type}) не співпадає з типом виразу ({when_expr_type})")
        else:
            break
    prev_ident()
    return


def parse_return_statement():
    global numRow, currentFunction
    indent = next_ident()
    print(f"{indent}parse_return_statement():")
    parse_token("return", "keyword")
    numLine, lex, tok = get_symb()
    
    return_type = None
    if lex not in ("}", ";"):
        return_type = parse_expression()
    else:
        return_type = 'Unit'
    
    # Перевірка типу return
    if currentFunction and currentFunction in tableOfFunc:
        expected_type = tableOfFunc[currentFunction]['return_type']
        if expected_type != return_type:
            if not (expected_type == 'Real' and return_type == 'Int'):
                fail_semantic("невідповідність типу return", (numLine, currentFunction, expected_type, return_type))
    
    prev_ident()
    return True


def parse_expression():
    return parse_logical_or_expr()


def parse_logical_or_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_logical_or_expr():")
    left_type = parse_logical_and_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex == "||" and tok == "logical_op":
            numRow += 1
            print(f"{indent}Логічний OR: {lex}")
            right_type = parse_logical_and_expr()
            result_type = get_type_op(left_type, '||', right_type)
            if result_type == 'type_error':
                fail_semantic("несумісність типів операндів", (numLine, '||', left_type, right_type))
            left_type = result_type
        else:
            break
    prev_ident()
    return left_type


def parse_logical_and_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_logical_and_expr():")
    left_type = parse_equality_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex == "&&" and tok == "logical_op":
            numRow += 1
            print(f"{indent}Логічний AND: {lex}")
            right_type = parse_equality_expr()
            result_type = get_type_op(left_type, '&&', right_type)
            if result_type == 'type_error':
                fail_semantic("несумісність типів операндів", (numLine, '&&', left_type, right_type))
            left_type = result_type
        else:
            break
    prev_ident()
    return left_type


def parse_equality_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_equality_expr():")
    left_type = parse_relational_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex in ("==", "!=") and tok == "rel_op":
            numRow += 1
            print(f"{indent}Оператор порівняння: {lex}")
            right_type = parse_relational_expr()
            result_type = get_type_op(left_type, lex, right_type)
            if result_type == 'type_error':
                fail_semantic("несумісність типів операндів", (numLine, lex, left_type, right_type))
            left_type = result_type
        else:
            break
    prev_ident()
    return left_type


def parse_relational_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_relational_expr():")
    left_type = parse_add_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex in ("<", "<=", ">", ">=") and tok == "rel_op":
            numRow += 1
            print(f"{indent}Оператор відношення: {lex}")
            right_type = parse_add_expr()
            result_type = get_type_op(left_type, lex, right_type)
            if result_type == 'type_error':
                fail_semantic("несумісність типів операндів", (numLine, lex, left_type, right_type))
            left_type = result_type
        else:
            break
    prev_ident()
    return left_type


def parse_add_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_add_expr():")
    left_type = parse_mult_expr()
    while True:
        numLine, lex, tok = get_symb()
        if tok == "add_op":
            numRow += 1
            print(f"{indent}Арифметичний оператор: {lex}")
            right_type = parse_mult_expr()
            result_type = get_type_op(left_type, lex, right_type)
            if result_type == 'type_error':
                fail_semantic("несумісність типів операндів", (numLine, lex, left_type, right_type))
            left_type = result_type
        else:
            break
    prev_ident()
    return left_type


def parse_mult_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_mult_expr():")
    left_type = parse_power_expr()
    while True:
        numLine, lex, tok = get_symb()
        if tok == "mult_op":
            numRow += 1
            print(f"{indent}Арифметичний оператор: {lex}")
            right_type = parse_power_expr()
            result_type = get_type_op(left_type, lex, right_type)
            if result_type == 'type_error':
                fail_semantic("несумісність типів операндів", (numLine, lex, left_type, right_type))
            left_type = result_type
        else:
            break
    prev_ident()
    return left_type


def parse_power_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_power_expr():")
    left_type = parse_unary_expr()
    while True:
        numLine, lex, tok = get_symb()
        if tok == "exp_op":
            numRow += 1
            print(f"{indent}Оператор піднесення до степеня: {lex}")
            right_type = parse_unary_expr()
            result_type = get_type_op(left_type, lex, right_type)
            if result_type == 'type_error':
                fail_semantic("несумісність типів операндів", (numLine, lex, left_type, right_type))
            left_type = result_type
        else:
            break
    prev_ident()
    return left_type


def parse_unary_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_unary_expr():")
    _, lex, tok = get_symb()
    unary_op = None
    if (lex in ("+", "-") and tok == "add_op") or (lex == "!" and tok == "logical_op"):
        print(f"{indent}Унарний оператор: {lex}")
        unary_op = lex
        numRow += 1
    
    expr_type = parse_primary_expr()
    
    # Перевірка типу для унарних операторів
    if unary_op:
        if unary_op in ('+', '-'):
            if expr_type not in ('Int', 'Real'):
                print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Унарний {unary_op} застосовано до типу {expr_type}")
        elif unary_op == '!':
            if expr_type != 'Boolean':
                print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Унарний ! застосовано до типу {expr_type}")
    
    prev_ident()
    return expr_type


def parse_primary_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parsePrimaryExpr():")
    numLine, lex, tok = get_symb()
    
    if lex == "if" and tok == "keyword":
        expr_type = parse_if_expression()
        prev_ident()
        return expr_type
    
    if tok in ("int_const", "real_const", "string_const", "bool_const"):
        numRow += 1
        trace(f"{indent}  Const: ({lex}, {tok})")
        if tok == "int_const":
            result_type = 'Int'
        elif tok == "real_const":
            result_type = 'Real'
        elif tok == "string_const":
            result_type = 'String'
        elif tok == "bool_const":
            result_type = 'Boolean'
        prev_ident()
        return result_type
    
    if tok == "identifier" or (lex.startswith("`") and lex.endswith("`")) or (tok == 'keyword' and lex in ('readLine', 'print')):
        trace(f"{indent}Identifier/FunctionCall/Print: {lex}")
        identifier = lex
        numRow += 1
        numLine, lex2, tok2 = get_symb()
        
        if lex2 == "(" and tok2 == "brackets_op":
            numRow += 1
            if identifier == "readLine":
                numLine3, lex3, tok3 = get_symb()
                if lex3 != ")" or tok3 != "brackets_op":
                    fail_parse("readLine() має бути без параметрів", (numLine3, lex3, tok3, ")", "brackets_op"))
                parse_token(")", "brackets_op")
                prev_ident()
                return 'String'
            else:
                # Виклик функції
                if identifier not in tableOfFunc:
                    fail_semantic("використання неоголошеної функції", (numLine, identifier))
                
                func_info = tableOfFunc[identifier]
                arg_types = parse_arguments()
                parse_token(")", "brackets_op")
                
                # Перевірка кількості параметрів
                expected_params = len(func_info['params'])
                actual_params = len(arg_types)
                
                required_params = sum(1 for p in func_info['params'] if not p[2])
                if actual_params < required_params or actual_params > expected_params:
                    fail_semantic("невідповідність кількості параметрів", 
                                (numLine, identifier, expected_params, actual_params))
                
                # Перевірка типів параметрів
                for i, (arg_type, param_info) in enumerate(zip(arg_types, func_info['params'])):
                    param_name, param_type, has_default = param_info
                    if arg_type != param_type:
                        if not (param_type == 'Real' and arg_type == 'Int'):
                            fail_semantic("невідповідність типів параметрів", 
                                        (numLine, identifier, i+1, param_type, arg_type))
                
                prev_ident()
                return func_info['return_type']
        else:
            # Просто змінна
            if identifier not in tableOfVar:
                fail_semantic("використання неоголошеної змінної", (numLine, identifier))
            
            if not is_var_initialized(identifier):
                fail_semantic("використання неініціалізованої змінної", (numLine, identifier))
            
            prev_ident()
            return get_type_var(identifier)
    
    if lex == "(" and tok == "brackets_op":
        numRow += 1
        expr_type = parse_expression()
        parse_token(")", "brackets_op")
        prev_ident()
        return expr_type
    
    fail_parse("невідповідність у PrimaryExpr",
               (numLine, lex, tok, "константа, ідентифікатор, ( або тернарний оператор if ... else"))


def parse_function_call():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_function_call():")
    numLine, lex, tok = get_symb()
    func_name = None
    if tok == "identifier":
        print(f"{indent}Виклик функції: {lex}")
        func_name = lex
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    
    # Семантична перевірка
    if func_name not in tableOfFunc:
        fail_semantic("використання неоголошеної функції", (numLine, func_name))
    
    parse_token("(", "brackets_op")
    arg_types = parse_arguments()
    parse_token(")", "brackets_op")
    
    # Перевірка параметрів
    func_info = tableOfFunc[func_name]
    expected_params = len(func_info['params'])
    actual_params = len(arg_types)
    
    required_params = sum(1 for p in func_info['params'] if not p[2])
    if actual_params < required_params or actual_params > expected_params:
        fail_semantic("невідповідність кількості параметрів", 
                    (numLine, func_name, expected_params, actual_params))
    
    for i, (arg_type, param_info) in enumerate(zip(arg_types, func_info['params'])):
        param_name, param_type, has_default = param_info
        if arg_type != param_type:
            if not (param_type == 'Real' and arg_type == 'Int'):
                fail_semantic("невідповідність типів параметрів", 
                            (numLine, func_name, i+1, param_type, arg_type))
    
    prev_ident()
    return True


def parse_arguments():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_arguments():")
    numLine, lex, tok = get_symb()
    arg_types = []
    
    if lex == ")" and tok == "brackets_op":
        prev_ident()
        return arg_types
    
    print(f"{indent}Аргумент: {lex}, {tok}")
    arg_type = parse_expression()
    arg_types.append(arg_type)
    
    while True:
        if numRow > len_tableOfSymb:
            break
        numLine, lex, tok = get_symb()
        if lex == "," and tok == "punct":
            numRow += 1
            if numRow > len_tableOfSymb:
                break
            numLine2, lex2, tok2 = get_symb()
            print(f"{indent}Аргумент: {lex2}, {tok2}")
            arg_type = parse_expression()
            arg_types.append(arg_type)
        else:
            break
    prev_ident()
    return arg_types


def parse_if_expression():
    indent = next_ident()
    print(f"{indent}parse_if_expression():")
    parse_token("if", "keyword")
    parse_token("(", "brackets_op")
    cond_type = parse_expression()
    if cond_type != 'Boolean':
        print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Умова if має бути Boolean, отримано {cond_type}")
    parse_token(")", "brackets_op")
    then_type = parse_expression()
    parse_token("else", "keyword")
    else_type = parse_expression()
    
    if then_type != else_type:
        if not ((then_type == 'Real' and else_type == 'Int') or (then_type == 'Int' and else_type == 'Real')):
            print(f"    [Semantic] ПОПЕРЕДЖЕННЯ: Гілки if-expression мають різні типи: {then_type} та {else_type}")
            result_type = then_type
        else:
            result_type = 'Real'
    else:
        result_type = then_type
    
    prev_ident()
    return result_type


def parse_return_statement():
    global numRow, currentFunction
    indent = next_ident()
    print(f"{indent}parse_return_statement():")
    parse_token("return", "keyword")
    numLine, lex, tok = get_symb()

    return_type = None
    if lex not in ("}", ";"):
        return_type = parse_expression()
    else:
        return_type = 'Unit'

    if currentFunction and currentFunction in tableOfFunc:
        expected_type = tableOfFunc[currentFunction]['return_type']
        if expected_type != return_type:
            if not (expected_type == 'Real' and return_type == 'Int'):
                fail_semantic("невідповідність типу return", (numLine, currentFunction, expected_type, return_type))

    prev_ident()
    return 'return'



print("\nЛЕКСИЧНИЙ АНАЛІЗ ПРОГРАМИ МОВОЮ QIRIM")
main_tbl = PrettyTable()
main_tbl.field_names = ["Рядок", "Лексема", "Токен", "Індекс"]
for _, (ln, lex, tok, idx) in tableOfSymb.items():
    main_tbl.add_row([ln, lex, tok, idx])
print(main_tbl)
print(statusMessage)

if len(tableOfSymb) > 0 and FSuccess[1]:
    print("\nСИНТАКСИЧНИЙ ТА СЕМАНТИЧНИЙ АНАЛІЗ ПРОГРАМИ МОВОЮ QIRIM\n")
    try:
        parse_program()
        
        # Вивід таблиць після успішного аналізу
        print("\n" + "="*80)
        print("ТАБЛИЦЯ ЗМІННИХ:")
        print("="*80)
        var_tbl = PrettyTable()
        var_tbl.field_names = ["Ім'я", "Тип", "Ініціалізована", "Змінна (var/val)", "Рядок"]
        for var_name, var_info in sorted(tableOfVar.items()):
            var_tbl.add_row([
                var_name,
                var_info['type'],
                "Так" if var_info['initialized'] else "Ні",
                "var" if var_info['mutable'] else "val",
                var_info['line']
            ])
        print(var_tbl)
        
        print("\n" + "="*80)
        print("ТАБЛИЦЯ ФУНКЦІЙ:")
        print("="*80)
        func_tbl = PrettyTable()
        func_tbl.field_names = ["Ім'я", "Параметри", "Тип повернення", "Рядок"]
        for func_name, func_info in sorted(tableOfFunc.items()):
            params_str = ", ".join([f"{p[0]}: {p[1]}" + (" = default" if p[2] else "") 
                                   for p in func_info['params']])
            if not params_str:
                params_str = "(без параметрів)"
            func_tbl.add_row([
                func_name,
                params_str,
                func_info['return_type'],
                func_info['line']
            ])
        print(func_tbl)
        
    except Exception as e:
        print(f"\nПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
else:
    if not FSuccess[1]:
        pass
    else:
        print("\nСинтаксичний аналіз НЕМОЖЛИВИЙ, оскільки таблиця символів пуста!")