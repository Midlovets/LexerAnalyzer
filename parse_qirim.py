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


def next_ident():
    global ident
    ident += stepIdent
    return " " * ident


def prev_ident():
    global ident
    ident -= stepIdent
    return " " * ident


TRACE = False  # Увімкнути/вимкнути відлагоджувальні повідомлення


def trace(msg):
    if TRACE:
        print(msg)


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
        if numRow == len_tableOfSymb + 1:  # Чи всі токени використані
            print("\nСинтаксичний аналіз завершився успішно!")
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
    global numRow
    indent = next_ident()
    print(f"{indent}parse_main_function():")
    parse_token("fun", "keyword")
    parse_token("main", "keyword")
    parse_token("(", "brackets_op")
    parse_token(")", "brackets_op")
    parse_block(is_function_block=True, function_name="main")
    prev_ident()
    return True


def parse_function_declaration():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_function_declaration():")
    parse_token("fun", "keyword")
    numLine, lex, tok = get_symb()
    if tok == "identifier":
        print(f"{indent}Ім'я функції: {lex}")
        function_name = lex
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    parse_token("(", "brackets_op")
    numLine, lex, tok = get_symb()
    if lex != ")":  # Якщо виклик не пустий - після "(" йде щось, але не ")"
        parse_params()
    parse_token(")", "brackets_op")
    numLine, lex, tok = get_symb()
    if lex == ":" and tok == "punct":  # Якщо є тип повернення
        numRow += 1
        parse_return_type()
    # FunctionBody
    numLine, lex, tok = get_symb()
    if lex == "=" and tok == "assign_op":
        numRow += 1
        parse_expression()
    elif lex == "{" and tok == "brackets_op":
        parse_block(is_function_block=True, function_name=function_name)
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "= або {", "(assign_op або brackets_op)"))
    prev_ident()
    return True


def parse_params():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_params():")
    parse_param()
    while True:
        numLine, lex, tok = get_symb()
        if lex == "," and tok == "punct":  # Якщо не один параметр
            numRow += 1
            parse_param()
        else:
            break
    prev_ident()
    return True


def parse_param():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_param():")
    numLine, lex, tok = get_symb()
    if tok == "identifier":
        print(f"{indent}Параметр: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    parse_token(":", "punct")  # Тип параметра обов'язково має бути вказаний
    parse_type()
    numLine, lex, tok = get_symb()
    if lex == "=" and tok == "assign_op":  # Якщо є значення за замовчуванням
        numRow += 1
        parse_expression()
    prev_ident()
    return True


def parse_type():
    global numRow
    indent = next_ident()
    numLine, lex, tok = get_symb()
    if tok == "type" or (lex == "Unit" and tok == "keyword"):
        print(f"{indent}Тип: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "type", "type"))
    prev_ident()
    return True


def parse_return_type():
    global numRow
    indent = next_ident()
    numLine, lex, tok = get_symb()
    if tok == "type" or (lex == "Unit" and tok == "keyword"):
        print(f"{indent}Тип повернення: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "type або Unit", "type"))
    prev_ident()
    return True


def parse_function_body():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_function_body():")
    numLine, lex, tok = get_symb()
    if lex == "=" and tok == "assign_op":  # Якщо функція записана в одному рядку
        numRow += 1
        parse_expression()
    elif lex == "{" and tok == "brackets_op":
        parse_block()
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "= або {", "assign_op або brackets_op"))
    prev_ident()
    return True


def parse_block(is_function_block=False, function_name=None):
    global numRow
    indent = next_ident()
    print(f"{indent}parse_block():")
    parse_token("{", "brackets_op")
    while True:
        if numRow > len_tableOfSymb:
            if is_function_block:
                print(f"Parser ERROR: Незакрита функція {function_name if function_name else ""}")
                exit(1010)
            else:
                print("ПОМИЛКА! Очікувався: '}'.")
                exit(1009)
        numLine, lex, tok = get_symb()
        if lex == "}" and tok == "brackets_op":
            break
        if not parse_function_statement(is_function_block, function_name):
            break
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
    if is_function_block and lex == "fun" and tok == "keyword":  # Якщо оголошено функцію в блоці іншої функції
        print(
            f"Parser ERROR: Вкладене оголошення функції у тілі функції '{function_name if function_name else ''}' не дозволено.")
        exit(1011)
    if lex == "}" and tok == "brackets_op":
        prev_ident()
        return False
    if lex in ("val", "var") and tok == "keyword":
        parse_variable_declarations()
    elif lex == "return" and tok == "keyword":
        parse_return_statement()
    else:
        parse_statement_section(is_function_block, function_name)
    prev_ident()
    return True


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
    if lex in ("var", "val") and tok == "keyword":
        print(f"{indent}Тип оголошення: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "var або val", "keyword"))
    parse_declaration()
    prev_ident()
    return True


def parse_declaration():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_declaration():")
    numLine, lex, tok = get_symb()
    if tok == "identifier":
        print(f"{indent}Змінна: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, 'identifier', 'identifier'))
    numLine, lex, tok = get_symb()
    if lex == ":" and tok == "punct":
        numRow += 1
        parse_type()
        numLine, lex, tok = get_symb()
        if lex == "=" and tok == "assign_op":
            numRow += 1
            parse_expression()
    elif lex == "=" and tok == "assign_op":
        numRow += 1
        parse_expression()
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "var/val, : або =", 'punct або assign_op'))
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
    if tok == "identifier":
        print(f"{indent}Змінна: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    parse_token("=", "assign_op")
    parse_expression()
    prev_ident()
    return True


def parse_input_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_input_statement():")
    numLine, lex, tok = get_symb()
    if tok == "identifier":
        print(f"{indent}Змінна вводу: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    parse_token("=", "assign_op")
    parse_token("readLine", "keyword")
    parse_token("(", "brackets_op")
    parse_token(")", "brackets_op")
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
        if tok == "string_const" and ("${" in lex):  # Обробка рядків
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
    if tok == "identifier":
        print(f"{indent}Змінна циклу: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
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
    parse_expression()
    numLine, lex, tok = get_symb()
    if lex == ".." and tok == "punct":  # Діапазонний вираз
        numRow += 1
        parse_expression()
        numLine, lex, tok = get_symb()
    elif lex == "downTo" and tok == "keyword":
        numRow += 1
        parse_expression()
        numLine, lex, tok = get_symb()
    if lex == "step" and tok == "keyword":  # step може бути після діапазону або одразу після першого виразу
        numRow += 1
        parse_step_expr()
    elif lex not in (")", "step"):  # Якщо не було діапазону і не було step, це помилка
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
    parse_expression()
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
    parse_expression()
    parse_token(")", "brackets_op")
    prev_ident()
    return True


def parse_if_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_if_statement():")

    parse_token("if", "keyword")
    parse_token("(", "brackets_op")
    parse_expression()
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
    parse_expression()
    parse_token(")", "brackets_op")
    parse_token("{", "brackets_op")
    parse_when_entry()
    while True:
        if numRow > len_tableOfSymb:
            fail_parse("Незакритий оператор when", (None, None, None))
        numLine, lex, tok = get_symb()
        if lex == "}" and tok == "brackets_op":
            break
        parse_when_entry()
    parse_token("}", "brackets_op")
    prev_ident()
    return True


def parse_when_entry():
    indent = next_ident()
    print(f"{indent}parse_when_entry():")
    parse_when_condition()
    parse_token('->', 'punct')
    parse_do_block()
    prev_ident()
    return True


def parse_when_condition():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_when_condition():")

    _, lex, tok = get_symb()
    if lex == "else" and tok == "keyword":
        numRow += 1
        prev_ident()
        return

    parse_expression()
    while True:
        _, lex, tok = get_symb()
        if lex == "," and tok == "punct":
            numRow += 1
            parse_expression()
        else:
            break
    prev_ident()
    return


def parse_return_statement():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_return_statement():")
    parse_token("return", "keyword")
    numLine, lex, tok = get_symb()
    if lex not in ("}", ";"):
        parse_expression()
    prev_ident()
    return True


def parse_expression():
    return parse_logical_or_expr()


def parse_logical_or_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_logical_or_expr():")
    parse_logical_and_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex == "||" and tok == "logical_op":
            numRow += 1
            print(f"{indent}Логічний OR: {lex}")
            parse_logical_and_expr()
        else:
            break
    prev_ident()
    return True


def parse_logical_and_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_logical_and_expr():")
    parse_equality_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex == "&&" and tok == "logical_op":
            numRow += 1
            print(f"{indent}Логічний AND: {lex}")
            parse_equality_expr()
        else:
            break
    prev_ident()
    return True


def parse_equality_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_equality_expr():")
    parse_relational_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex in ("==", "!=") and tok == "rel_op":
            numRow += 1
            print(f"{indent}Оператор порівняння: {lex}")
            parse_relational_expr()
        else:
            break
    prev_ident()
    return True


def parse_relational_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_relational_expr():")
    parse_add_expr()
    while True:
        numLine, lex, tok = get_symb()
        if lex in ("<", "<=", ">", ">=") and tok == "rel_op":
            numRow += 1
            print(f"{indent}Оператор відношення: {lex}")
            parse_add_expr()
        else:
            break
    prev_ident()
    return True


def parse_add_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_add_expr():")
    parse_mult_expr()
    while True:
        numLine, lex, tok = get_symb()
        if tok == "add_op":
            numRow += 1
            print(f"{indent}Арифметичний оператор: {lex}")
            parse_mult_expr()
        else:
            break
    prev_ident()
    return True


def parse_mult_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_mult_expr():")
    parse_power_expr()
    while True:
        numLine, lex, tok = get_symb()
        if tok == "mult_op":
            numRow += 1
            print(f"{indent}Арифметичний оператор: {lex}")
            parse_power_expr()
        else:
            break
    prev_ident()
    return True


def parse_power_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_power_expr():")
    parse_unary_expr()
    while True:
        numLine, lex, tok = get_symb()
        if tok == "exp_op":
            numRow += 1
            print(f"{indent}Оператор піднесення до степеня: {lex}")
            parse_unary_expr()
        else:
            break
    prev_ident()
    return True


def parse_unary_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_unary_expr():")
    _, lex, tok = get_symb()
    if (lex in ("+", "-") and tok == "add_op") or (lex == "!" and tok == "logical_op"):
        print(f"{indent}Унарний оператор: {lex}")
        numRow += 1
    parse_primary_expr()
    prev_ident()
    return True


def parse_primary_expr():
    global numRow
    indent = next_ident()
    trace(f"{indent}parsePrimaryExpr():")
    numLine, lex, tok = get_symb()
    if lex == "if" and tok == "keyword":  # IfExpression
        parse_if_expression()
        prev_ident()
        return True
    if tok in ("int_const", "real_const", "string_const", "bool_const"):  # Const
        numRow += 1
        trace(f"{indent}  Const: ({lex}, {tok})")
        prev_ident()
        return True
    if tok == "identifier" or (lex.startswith("`") and lex.endswith("`")) or (tok == 'keyword' and lex in (
            'readLine', 'print')):  # Identifier, FunctionCall, readLine або print statement
        trace(f"{indent}Identifier/FunctionCall/Print: {lex}")
        numRow += 1
        numLine, lex2, tok2 = get_symb()
        if lex2 == "(" and tok2 == "brackets_op":
            numRow += 1
            if lex == "readLine":
                numLine3, lex3, tok3 = get_symb()
                if lex3 != ")" or tok3 != "brackets_op":
                    fail_parse("readLine() має бути без параметрів", (numLine3, lex3, tok3, ")", "brackets_op"))
            else:
                parse_arguments()
            parse_token(")", "brackets_op")
        prev_ident()
        return True
    if lex == "(" and tok == "brackets_op":  # '(' Expression ')'
        numRow += 1
        parse_expression()
        parse_token(")", "brackets_op")
        prev_ident()
        return True
    fail_parse("невідповідність у PrimaryExpr",
               (numLine, lex, tok, "константа, ідентифікатор, ( або тернарний оператор if ... else"))


def parse_function_call():
    global numRow
    indent = next_ident()
    print(f"{indent}parse_function_call():")
    numLine, lex, tok = get_symb()
    if tok == "identifier":
        print(f"{indent}Виклик функції: {lex}")
        numRow += 1
    else:
        fail_parse("несумісність токенів", (numLine, lex, tok, "identifier", "identifier"))
    parse_token("(", "brackets_op")
    parse_arguments()
    parse_token(")", "brackets_op")
    prev_ident()
    return True


def parse_arguments():
    global numRow
    indent = next_ident()
    trace(f"{indent}parse_arguments():")
    numLine, lex, tok = get_symb()
    if lex == ")" and tok == "brackets_op":  # Порожній список аргументів
        prev_ident()
        return True
    print(f"{indent}Аргумент: {lex}, {tok}")
    parse_expression()
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
            parse_expression()
        else:
            break
    prev_ident()
    return True


def parse_if_expression():
    indent = next_ident()
    print(f"{indent}parse_if_expression():")
    parse_token("if", "keyword")
    parse_token("(", "brackets_op")
    parse_expression()
    parse_token(")", "brackets_op")
    parse_expression()
    parse_token("else", "keyword")
    parse_expression()
    prev_ident()
    return True


print("\nЛЕКСИЧНИЙ АНАЛІЗ ПРОГРАМИ МОВОЮ QIRIM")  # Вивід таблиці токенів перед синтаксичним аналізом
main_tbl = PrettyTable()
main_tbl.field_names = ["Рядок", "Лексема", "Токен", "Індекс"]
for _, (ln, lex, tok, idx) in tableOfSymb.items():
    main_tbl.add_row([ln, lex, tok, idx])
print(main_tbl)
print(statusMessage)

if len(tableOfSymb) > 0 and FSuccess[1]:  # Перевірка перед синтаксичним аналізом
    print("\nСИНТАКСИЧНИЙ АНАЛІЗ ПРОГРАМИ МОВОЮ QIRIM\n")
    try:
        parse_program()
    except Exception as e:
        print(f"\nПОМИЛКА: {e}")
        import traceback

        traceback.print_exc()
else:
    if not FSuccess[1]:  # Вивід повідомлення лексичного аналізатора
        pass
    else:
        print("\nСинтаксичний аналіз НЕМОЖЛИВИЙ, оскільки таблиця символів пуста!")