import lex_qirim

lex_qirim.lex()

tableOfSymb = lex_qirim.tableOfSymb
tableOfId = lex_qirim.tableOfId
tableOfConst = lex_qirim.tableOfConst
statusMessage = lex_qirim.statusMessage
FSuccess = lex_qirim.FSuccess


len_tableOfSymb = len(tableOfSymb)

numRow = 1

stepIndt = 2
indt = 0


def nextIndt():
    global indt
    indt += stepIndt
    return ' ' * indt


def predIndt():
    global indt
    indt -= stepIndt
    return ' ' * indt


# Enable/disable parser trace output (set False to quiet)
TRACE = False


def trace(msg):
    if TRACE:
        print(msg)


def getSymb():
    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', numRow)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


def failParse(msg, data):
    if msg == 'неочікуваний кінець програми':
        row = data
        print('\nParser ERROR:')
        print(f'  Неочікуваний кінець програми — у таблиці символів немає запису з номером {row}.')
        if row > 1:
            print(f'  Останній запис: {tableOfSymb[row - 1]}')
        exit(1002)
    elif msg == 'несумісність токенів':
        numLine, lexeme, token, expected_lex, expected_tok = data
        print('\nParser ERROR:')
        print(f'  У рядку {numLine} знайдено несподіваний елемент ({lexeme}, {token}).')
        print(f'  Очікувалося: ({expected_lex}, {expected_tok})')
        exit(1003)
    else:
        print(f'\nParser ERROR: {msg}')
        print(f'  Дані: {data}')
        exit(1004)


def parseToken(lexeme, token):
    global numRow
    indent = nextIndt()

    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))

    numLine, lex, tok = getSymb()
    numRow += 1

    print(f"{indent}parseToken: В рядку {numLine} - токен ({lex}, {tok})")
    trace(f'{indent}  очікувалося: ({lexeme}, {token})')

    if (lex, tok) == (lexeme, token):
        res = True
    else:
        failParse('несумісність токенів', (numLine, lex, tok, lexeme, token))
        res = False

    predIndt()
    return res

# ============= ПОВНА ГРАМАТИКА МОВИ QIRIM =============
# Program = { FunctionDeclaration } MainFunction { FunctionDeclaration }
# MainFunction = 'fun' 'main' '(' ')' Block
# VariableDeclarations = VariableDeclaration { ';' VariableDeclaration }
# VariableDeclaration  = ('var' | 'val' ) Declaration
# Declaration = Identifier ( ':' Type [ '=' Expression ] | '=' Expression )
# Type = Int | Real | Boolean | String
# FunctionDeclaration = 'fun' Identifier '(' [ Parameters ] ')' [ ':' ReturnType ] FunctionBody
# Parameters = Parameter { ',' Parameter }
# Parameter = Identifier ':' Type [ '=' Expression ]
# FunctionBody = Block | '=' Expression
# Block = '{' { FunctionStatement } '}'
# ReturnType = Type | Unit
# FunctionStatement = VariableDeclarations | StatementSection | ReturnStatement
# ReturnStatement = 'return' [ Expression ]
# Expression = LogicalOrExpr
# LogicalOrExpr = LogicalAndExpr { '||' LogicalAndExpr }
# LogicalAndExpr = EqualityExpr { '&&' EqualityExpr }
# EqualityExpr = RelationalExpr { ( '==' | '!=' ) RelationalExpr }
# RelationalExpr = AddExpr { ( '<' | '<=' | '>' | '>=' ) AddExpr }
# AddExpr = MultExpr { ( '+' | '-' ) MultExpr }
# MultExpr = PowerExpr { ( '*' | '/' | '%' ) PowerExpr }
# PowerExpr = UnaryExpr { '**' UnaryExpr }
# UnaryExpr = [ '+' | '-' | '!' ] PrimaryExpr
# PrimaryExpr = Const | Identifier | FunctionCall | '(' Expression ')' | IfExpression
# FunctionCall = Identifier '(' [ Arguments ] ')'
# Arguments = Expression { ',' Expression }
# StatementSection = Statement { ';' Statement }
# Statement = AssignmentStatement | InputStatement | OutputStatement | LoopStatement | BranchingStatement | FunctionCallStatement
# AssignmentStatement = Identifier '=' Expression
# InputStatement = Identifier '=' readLine '(' ')'
# OutputStatement = 'print' '(' [Expression] ')'
# LoopStatement = ForStatement | WhileStatement | DoWhileStatement
# ForStatement = 'for' '(' Identifier 'in' ForRange ')' DoBlock
# ForRange = Expression ('..' | 'downTo') Expression [ StepExpr ]
# StepExpr = 'step' Expression
# DoBlock = Statement | '{' StatementSection '}'
# WhileStatement = while '(' Expression ')' DoBlock
# DoWhileStatement = do DoBlock while '(' Expression ')'
# BranchingStatement = IfStatement | WhenStatement
# IfStatement = 'if' '(' Expression ')' DoBlock [ 'else' DoBlock ]
# IfExpression = 'if' '(' Expression ')' Expression 'else' Expression
# WhenStatement = 'when' '(' Expression ')' '{' WhenEntry { WhenEntry } '}'
# WhenEntry = WhenCondition '->' DoBlock
# WhenCondition = Expression { ',' Expression } | 'else'

def parseProgram():
    """Program = { FunctionDeclaration } MainFunction { FunctionDeclaration }"""
    try:
        indent = nextIndt()
        print(f'{indent}parseProgram():')
        
        while numRow <= len_tableOfSymb:
            numLine, lex, tok = getSymb()
            if lex == 'fun' and tok == 'keyword':

                if numRow + 1 <= len_tableOfSymb:
                    _, next_lex, next_tok, _ = tableOfSymb[numRow + 1]
                    if next_lex == 'main' and next_tok == 'keyword':
                        break  
                parseFunctionDeclaration()
            else:
                break

        parseMainFunction()

        while numRow <= len_tableOfSymb:
            numLine, lex, tok = getSymb()
            if lex == 'fun' and tok == 'keyword':
                parseFunctionDeclaration()
            else:
                break
        
        print('\n' + '=' * 50)
        print('Parser: Синтаксичний аналіз завершився успішно!')
        print('=' * 50)
        return True
    except SystemExit as e:
        print(f'\nParser: Аварійне завершення програми з кодом {e}')
        return False
    finally:
        predIndt()


def parseMainFunction():
    """MainFunction = 'fun' 'main' '(' ')' Block"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseMainFunction():')
    
    parseToken('fun', 'keyword')
    parseToken('main', 'keyword')
    parseToken('(', 'brackets_op')
    parseToken(')', 'brackets_op')
    parseBlock()
    
    predIndt()
    return True


def parseFunctionDeclaration():
    """FunctionDeclaration = 'fun' Identifier '(' [ Parameters ] ')' [ ':' ReturnType ] FunctionBody"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseFunctionDeclaration():')
    
    parseToken('fun', 'keyword')
    

    numLine, lex, tok = getSymb()
    if tok == 'identifier':
        print(f"{indent}  Ім'я функції: {lex}")
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'identifier', 'identifier'))
    
    parseToken('(', 'brackets_op')
    
    # Опціональні параметри
    numLine, lex, tok = getSymb()
    if lex != ')':
        parseParameters()
    
    parseToken(')', 'brackets_op')
    
    # Опціональний тип повернення
    numLine, lex, tok = getSymb()
    if lex == ':' and tok == 'punct':
        numRow += 1
        parseReturnType()
    
    # FunctionBody
    parseFunctionBody()
    
    predIndt()
    return True


def parseParameters():
    """Parameters = Parameter { ',' Parameter }"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseParameters():')
    
    parseParameter()
    
    while True:
        numLine, lex, tok = getSymb()
        if lex == ',' and tok == 'punct':
            numRow += 1
            parseParameter()
        else:
            break
    
    predIndt()
    return True


def parseParameter():
    """Parameter = Identifier ':' Type [ '=' Expression ]"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseParameter():')
    
    numLine, lex, tok = getSymb()
    if tok == 'identifier':
        print(f'{indent}  Параметр: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'identifier', 'identifier'))
    
    parseToken(':', 'punct')
    parseType()
    
    # Опціональне значення за замовчуванням
    numLine, lex, tok = getSymb()
    if lex == '=' and tok == 'assign_op':
        numRow += 1
        parseExpression()
    
    predIndt()
    return True


def parseType():
    """Type = Int | Real | Boolean | String"""
    global numRow
    indent = nextIndt()
    
    numLine, lex, tok = getSymb()
    if tok == 'type':
        print(f'{indent}  Тип: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'type', 'type'))
    
    predIndt()
    return True


def parseReturnType():
    """ReturnType = Type | Unit"""
    global numRow
    indent = nextIndt()
    
    numLine, lex, tok = getSymb()
    if tok == 'type' or (lex == 'Unit' and tok == 'keyword'):
        print(f'{indent}  Тип повернення: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'type or Unit', 'type'))
    
    predIndt()
    return True


def parseFunctionBody():
    """FunctionBody = Block | '=' Expression"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseFunctionBody():')
    
    numLine, lex, tok = getSymb()
    if lex == '=' and tok == 'assign_op':
        numRow += 1
        parseExpression()
    elif lex == '{' and tok == 'brackets_op':
        parseBlock()
    else:
        failParse('несумісність токенів', (numLine, lex, tok, '= or {', 'assign_op or brackets_op'))
    
    predIndt()
    return True


def parseBlock():
    """Block = '{' { FunctionStatement } '}'"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseBlock():')
    
    parseToken('{', 'brackets_op')
    
    while True:
        numLine, lex, tok = getSymb()
        if lex == '}' and tok == 'brackets_op':
            break
        if not parseFunctionStatement():
            break
    
    parseToken('}', 'brackets_op')
    
    predIndt()
    return True


def parseFunctionStatement():
    """FunctionStatement = VariableDeclarations | StatementSection | ReturnStatement"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseFunctionStatement():')
    
    if numRow > len_tableOfSymb:
        predIndt()
        return False
    
    numLine, lex, tok = getSymb()
    
    if lex == '}' and tok == 'brackets_op':
        predIndt()
        return False
    
    # VariableDeclarations
    if lex in ('val', 'var') and tok == 'keyword':
        parseVariableDeclarations()
    # ReturnStatement
    elif lex == 'return' and tok == 'keyword':
        parseReturnStatement()
    # StatementSection
    else:
        parseStatementSection()
    
    predIndt()
    return True


def parseVariableDeclarations():
    """VariableDeclarations = VariableDeclaration { ';' VariableDeclaration }"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseVariableDeclarations():')
    
    parseVariableDeclaration()
    
    while True:
        numLine, lex, tok = getSymb()
        if lex == ';' and tok == 'punct':
            numRow += 1
            numLine, lex, tok = getSymb()
            if lex in ('val', 'var') and tok == 'keyword':
                parseVariableDeclaration()
            else:
                break
        else:
            break
    
    predIndt()
    return True


def parseVariableDeclaration():
    """VariableDeclaration = ('var' | 'val') Declaration"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseVariableDeclaration():')
    
    numLine, lex, tok = getSymb()
    if lex in ('var', 'val') and tok == 'keyword':
        print(f'{indent}  Тип оголошення: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'var or val', 'keyword'))
    
    parseDeclaration()
    
    predIndt()
    return True


def parseDeclaration():
    """Declaration = Identifier ( ':' Type [ '=' Expression ] | '=' Expression )"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseDeclaration():')
    
    numLine, lex, tok = getSymb()
    if tok == 'identifier':
        print(f'{indent}  Змінна: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'identifier', 'identifier'))
    
    numLine, lex, tok = getSymb()
    if lex == ':' and tok == 'punct':
        numRow += 1
        parseType()
        # Опціональна ініціалізація
        numLine, lex, tok = getSymb()
        if lex == '=' and tok == 'assign_op':
            numRow += 1
            parseExpression()
    elif lex == '=' and tok == 'assign_op':
        numRow += 1
        parseExpression()
    else:
        failParse('несумісність токенів', (numLine, lex, tok, ': or =', 'punct or assign_op'))
    
    predIndt()
    return True


def parseStatementSection():
    """StatementSection = Statement { ';' Statement }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseStatementSection():')


    while True:
        numLine, lex, tok = getSymb()
        # Якщо зустріли закриваючу дужку — кінець секції
        if lex == '}' and tok == 'brackets_op':
            break
        # Пропускаємо необов'язкові крапки з комою
        if lex == ';' and tok == 'punct':
            numRow += 1
            continue
        if not parseStatement():
            break
    
    predIndt()
    return True


def parseStatement():
    """Statement = AssignmentStatement | InputStatement | OutputStatement | LoopStatement | BranchingStatement | FunctionCallStatement"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseStatement():')
    
    if numRow > len_tableOfSymb:
        predIndt()
        return False
    
    numLine, lex, tok = getSymb()
    
    if lex == '}' and tok == 'brackets_op':
        predIndt()
        return False
    
    # OutputStatement
    if lex == 'print' and tok == 'keyword':
        parseOutputStatement()
    # LoopStatement
    elif lex == 'for' and tok == 'keyword':
        parseForStatement()
    elif lex == 'while' and tok == 'keyword':
        parseWhileStatement()
    elif lex == 'do' and tok == 'keyword':
        parseDoWhileStatement()
    # BranchingStatement
    elif lex == 'if' and tok == 'keyword':
        parseIfStatement()
    elif lex == 'when' and tok == 'keyword':
        parseWhenStatement()
    # break/continue (частина LoopStatement)
    elif lex == 'break' and tok == 'keyword':
        numRow += 1
        print(f'{indent}  break statement')
    elif lex == 'continue' and tok == 'keyword':
        numRow += 1
        print(f'{indent}  continue statement')
    # AssignmentStatement або InputStatement або FunctionCallStatement
    elif tok == 'identifier':
        # Дивимося наперед
        if numRow + 1 <= len_tableOfSymb:
            _, next_lex, next_tok, _ = tableOfSymb[numRow + 1]
            if next_lex == '=' and next_tok == 'assign_op':
                # Перевіряємо чи це InputStatement
                if numRow + 2 <= len_tableOfSymb:
                    _, after_eq_lex, after_eq_tok, _ = tableOfSymb[numRow + 2]
                    if after_eq_lex == 'readLine' and after_eq_tok == 'keyword':
                        parseInputStatement()
                    else:
                        parseAssignmentStatement()
                else:
                    parseAssignmentStatement()
            elif next_lex == '(' and next_tok == 'brackets_op':
                parseFunctionCallStatement()
            else:
                failParse('несумісність токенів', (numLine, lex, tok, '= or (', 'assign_op or brackets_op'))
        else:
            failParse('неочікуваний кінець програми', numRow)
    else:
        predIndt()
        return False
    
    predIndt()
    return True


def parseAssignmentStatement():
    """AssignmentStatement = Identifier '=' Expression"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseAssignmentStatement():')
    
    numLine, lex, tok = getSymb()
    if tok == 'identifier':
        print(f'{indent}  Змінна: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'identifier', 'identifier'))
    
    parseToken('=', 'assign_op')
    parseExpression()
    
    predIndt()
    return True


def parseInputStatement():
    """InputStatement = Identifier '=' 'readLine' '(' ')'"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseInputStatement():')
    
    numLine, lex, tok = getSymb()
    if tok == 'identifier':
        print(f'{indent}  Змінна вводу: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'identifier', 'identifier'))
    
    parseToken('=', 'assign_op')
    parseToken('readLine', 'keyword')
    parseToken('(', 'brackets_op')
    parseToken(')', 'brackets_op')
    
    predIndt()
    return True


def parseOutputStatement():
    """OutputStatement = 'print' '(' [Expression] ')'"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseOutputStatement():')
    
    parseToken('print', 'keyword')
    parseToken('(', 'brackets_op')
    
    numLine, lex, tok = getSymb()
    if lex != ')' or tok != 'brackets_op':
        parseExpression()
    
    parseToken(')', 'brackets_op')
    
    predIndt()
    return True


def parseFunctionCallStatement():
    """FunctionCallStatement = FunctionCall (викликає parseFunctionCall)"""
    indent = nextIndt()
    print(f'{indent}parseFunctionCallStatement():')
    parseFunctionCall()
    predIndt()
    return True


def parseForStatement():
    """ForStatement = 'for' '(' Identifier 'in' ForRange ')' DoBlock"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseForStatement():')
    
    parseToken('for', 'keyword')
    parseToken('(', 'brackets_op')
    
    numLine, lex, tok = getSymb()
    if tok == 'identifier':
        print(f'{indent}  Змінна циклу: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'identifier', 'identifier'))
    
    parseToken('in', 'keyword')
    parseForRange()
    parseToken(')', 'brackets_op')
    parseDoBlock()
    
    predIndt()
    return True


def parseForRange():
    """ForRange = Expression ('..' | 'downTo') Expression [ StepExpr ]"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseForRange():')
    
    parseExpression()
    
    numLine, lex, tok = getSymb()

    #  1) Expression '..' Expression [ 'downTo' Expression ]
    #  2) Expression 'downTo' Expression
    if lex == '..' and tok == 'punct':

        numRow += 1

        numLine, lex, tok = getSymb()
        if lex == 'downTo' and tok == 'keyword':
            numRow += 1
            parseExpression()
    elif lex == 'downTo' and tok == 'keyword':

        numRow += 1
        parseExpression()
    else:
        failParse('несумісність токенів', (numLine, lex, tok, ".. or downTo", 'punct or keyword'))

    # Опціональний StepExpr 
    numLine, lex, tok = getSymb()
    if lex == 'step' and tok == 'keyword':
        parseStepExpr()
    
    predIndt()
    return True


def parseStepExpr():
    """StepExpr = 'step' Expression"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseStepExpr():')
    
    parseToken('step', 'keyword')
    parseExpression()
    
    predIndt()
    return True


def parseDoBlock():
    """DoBlock = Statement | '{' StatementSection '}'"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseDoBlock():')
    
    numLine, lex, tok = getSymb()
    if lex == '{' and tok == 'brackets_op':
        numRow += 1
        parseStatementSection()
        parseToken('}', 'brackets_op')
    else:
        parseStatement()
    
    predIndt()
    return True


def parseWhileStatement():
    """WhileStatement = 'while' '(' Expression ')' DoBlock"""
    indent = nextIndt()
    print(f'{indent}parseWhileStatement():')
    
    parseToken('while', 'keyword')
    parseToken('(', 'brackets_op')
    parseExpression()
    parseToken(')', 'brackets_op')
    parseDoBlock()
    
    predIndt()
    return True


def parseDoWhileStatement():
    """DoWhileStatement = 'do' DoBlock 'while' '(' Expression ')'"""
    indent = nextIndt()
    print(f'{indent}parseDoWhileStatement():')
    
    parseToken('do', 'keyword')
    parseDoBlock()
    parseToken('while', 'keyword')
    parseToken('(', 'brackets_op')
    parseExpression()
    parseToken(')', 'brackets_op')
    
    predIndt()
    return True


def parseIfStatement():
    """IfStatement = 'if' '(' Expression ')' DoBlock [ 'else' DoBlock ]"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseIfStatement():')
    
    parseToken('if', 'keyword')
    parseToken('(', 'brackets_op')
    parseExpression()
    parseToken(')', 'brackets_op')
    parseDoBlock()
    
    numLine, lex, tok = getSymb()
    if lex == 'else' and tok == 'keyword':
        numRow += 1
        parseDoBlock()
    
    predIndt()
    return True


def parseWhenStatement():
    """WhenStatement = 'when' '(' Expression ')' '{' WhenEntry { WhenEntry } '}'"""
    indent = nextIndt()
    print(f'{indent}parseWhenStatement():')
    
    parseToken('when', 'keyword')
    parseToken('(', 'brackets_op')
    parseExpression()
    parseToken(')', 'brackets_op')
    parseToken('{', 'brackets_op')
    
    parseWhenEntry()
    while True:
        numLine, lex, tok = getSymb()
        if lex == '}' and tok == 'brackets_op':
            break
        parseWhenEntry()
    
    parseToken('}', 'brackets_op')
    
    predIndt()
    return True


def parseWhenEntry():
    """WhenEntry = WhenCondition '->' DoBlock"""
    indent = nextIndt()
    print(f'{indent}parseWhenEntry():')
    
    parseWhenCondition()
    parseToken('->', 'punct')
    parseDoBlock()
    
    predIndt()
    return True


def parseWhenCondition():
    """WhenCondition = Expression { ',' Expression } | 'else'"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseWhenCondition():')
    
    numLine, lex, tok = getSymb()
    if lex == 'else' and tok == 'keyword':
        numRow += 1
    else:
        parseExpression()
        while True:
            numLine, lex, tok = getSymb()
            if lex == ',' and tok == 'punct':
                numRow += 1
                parseExpression()
            else:
                break
    
    predIndt()
    return True


def parseReturnStatement():
    """ReturnStatement = 'return' [ Expression ]"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseReturnStatement():')
    
    parseToken('return', 'keyword')
    
    numLine, lex, tok = getSymb()

    if lex not in ('}', ';'):
        parseExpression()
    
    predIndt()
    return True


def parseExpression():
    """Expression = LogicalOrExpr"""
    return parseLogicalOrExpr()


def parseLogicalOrExpr():
    """LogicalOrExpr = LogicalAndExpr { '||' LogicalAndExpr }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseLogicalOrExpr():')
    
    parseLogicalAndExpr()
    
    while True:
        numLine, lex, tok = getSymb()
        if lex == '||' and tok == 'logical_op':
            numRow += 1
            print(f'{indent}  Логічний OR: {lex}')
            parseLogicalAndExpr()
        else:
            break
    
    predIndt()
    return True


def parseLogicalAndExpr():
    """LogicalAndExpr = EqualityExpr { '&&' EqualityExpr }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseLogicalAndExpr():')
    
    parseEqualityExpr()
    
    while True:
        numLine, lex, tok = getSymb()
        if lex == '&&' and tok == 'logical_op':
            numRow += 1
            print(f'{indent}  Логічний AND: {lex}')
            parseEqualityExpr()
        else:
            break
    
    predIndt()
    return True


def parseEqualityExpr():
    """EqualityExpr = RelationalExpr { ( '==' | '!=' ) RelationalExpr }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseEqualityExpr():')
    
    parseRelationalExpr()
    
    while True:
        numLine, lex, tok = getSymb()
        if lex in ('==', '!=') and tok == 'rel_op':
            numRow += 1
            print(f'{indent}  Оператор порівняння: {lex}')
            parseRelationalExpr()
        else:
            break
    
    predIndt()
    return True


def parseRelationalExpr():
    """RelationalExpr = AddExpr { ( '<' | '<=' | '>' | '>=' ) AddExpr }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseRelationalExpr():')
    
    parseAddExpr()
    
    while True:
        numLine, lex, tok = getSymb()
        if lex in ('<', '<=', '>', '>=') and tok == 'rel_op':
            numRow += 1
            print(f'{indent}  Оператор відношення: {lex}')
            parseAddExpr()
        else:
            break
    
    predIndt()
    return True


def parseAddExpr():
    """AddExpr = MultExpr { ( '+' | '-' ) MultExpr }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseAddExpr():')
    
    parseMultExpr()
    
    while True:
        numLine, lex, tok = getSymb()
        if tok == 'add_op':
            numRow += 1
            print(f'{indent}  Аритм. оператор: {lex}')
            parseMultExpr()
        else:
            break
    
    predIndt()
    return True


def parseMultExpr():
    """MultExpr = PowerExpr { ( '*' | '/' | '%' ) PowerExpr }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseMultExpr():')
    
    parsePowerExpr()
    
    while True:
        numLine, lex, tok = getSymb()
        if tok == 'mult_op':
            numRow += 1
            print(f'{indent}  Аритм. оператор: {lex}')
            parsePowerExpr()
        else:
            break
    
    predIndt()
    return True


def parsePowerExpr():
    """PowerExpr = UnaryExpr { '**' UnaryExpr }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parsePowerExpr():')
    
    parseUnaryExpr()
    
    while True:
        numLine, lex, tok = getSymb()
        if tok == 'exp_op':
            numRow += 1
            print(f'{indent}  Оператор степеня: {lex}')
            parseUnaryExpr()
        else:
            break
    
    predIndt()
    return True


def parseUnaryExpr():
    """UnaryExpr = [ '+' | '-' | '!' ] PrimaryExpr"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseUnaryExpr():')
    
    numLine, lex, tok = getSymb()
    if lex in ('+', '-') and tok == 'add_op':
        numRow += 1
        print(f'{indent}  Унарний оператор: {lex}')
    elif lex == '!' and tok == 'logical_op':
        numRow += 1
        print(f'{indent}  Унарний оператор: {lex}')
    
    parsePrimaryExpr()
    
    predIndt()
    return True


def parsePrimaryExpr():
    """PrimaryExpr = Const | Identifier | FunctionCall | '(' Expression ')' | IfExpression"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parsePrimaryExpr():')
    
    numLine, lex, tok = getSymb()
    
    # IfExpression
    if lex == 'if' and tok == 'keyword':
        parseIfExpression()
        predIndt()
        return True
    
    # Const
    if tok in ('int_const', 'real_const', 'string_const', 'bool_const'):
        numRow += 1
        trace(f'{indent}  Const: ({lex}, {tok})')
        predIndt()
        return True
    
    # Identifier or FunctionCall
    if tok == 'identifier':
        trace(f'{indent}  Identifier: {lex}')
        numRow += 1
        numLine, lex2, tok2 = getSymb()
        if lex2 == '(' and tok2 == 'brackets_op':
            # FunctionCall - парсимо аргументи
            numRow += 1
            parseArguments()
            parseToken(')', 'brackets_op')
        predIndt()
        return True
    
    # '(' Expression ')'
    if lex == '(' and tok == 'brackets_op':
        numRow += 1
        parseExpression()
        parseToken(')', 'brackets_op')
        predIndt()
        return True
    
    failParse('невідповідність у PrimaryExpr', (numLine, lex, tok, 'константа, ідентифікатор, ( або if'))


def parseFunctionCall():
    """FunctionCall = Identifier '(' [ Arguments ] ')'"""
    global numRow
    indent = nextIndt()
    print(f'{indent}parseFunctionCall():')
    
    numLine, lex, tok = getSymb()
    if tok == 'identifier':
        print(f'{indent}  Виклик функції: {lex}')
        numRow += 1
    else:
        failParse('несумісність токенів', (numLine, lex, tok, 'identifier', 'identifier'))
    
    parseToken('(', 'brackets_op')
    parseArguments()
    parseToken(')', 'brackets_op')
    
    predIndt()
    return True


def parseArguments():
    """Arguments = Expression { ',' Expression }"""
    global numRow
    indent = nextIndt()
    trace(f'{indent}parseArguments():')
    
    numLine, lex, tok = getSymb()
    if lex == ')' and tok == 'brackets_op':
        # Порожній список аргументів
        predIndt()
        return True
    
    parseExpression()
    
    while True:
        numLine, lex, tok = getSymb()
        if lex == ',' and tok == 'punct':
            numRow += 1
            parseExpression()
        else:
            break
    
    predIndt()
    return True


def parseIfExpression():
    """IfExpression = 'if' '(' Expression ')' Expression 'else' Expression"""
    indent = nextIndt()
    print(f'{indent}parseIfExpression():')
    
    parseToken('if', 'keyword')
    parseToken('(', 'brackets_op')
    parseExpression()
    parseToken(')', 'brackets_op')
    parseExpression()
    parseToken('else', 'keyword')
    parseExpression()
    
    predIndt()
    return True


from prettytable import PrettyTable

# Вивід таблиці токенів перед синтаксичним аналізом
print("\nЛЕКСИЧНИЙ АНАЛІЗ ПРОГРАМИ МОВОЮ QIRIM")
main_tbl = PrettyTable()
main_tbl.field_names = ["Рядок", "Лексема", "Токен", "Індекс"]
for _, (ln, lex, tok, idx) in tableOfSymb.items():
    main_tbl.add_row([ln, lex, tok, idx])
print(main_tbl)
print(statusMessage)

if FSuccess[1]:
    print('ТАБЛИЦІ:')

    symb = PrettyTable()
    symb.field_names = ["№", "Лексема", "Токен", "Індекс"]
    for key, (ln, lex, tok, idx) in tableOfSymb.items():
        symb.add_row([key, lex, tok, idx])
    print('Таблиця символів програми:')
    print(symb)

    ids = PrettyTable()
    ids.field_names = ["Індекс", "Ідентифікатор"]
    for lex, idx in sorted(tableOfId.items(), key=lambda x: x[1]):
        ids.add_row([idx, lex])
    print('\nТаблиця ідентифікаторів:')
    print(ids)

    consts = PrettyTable()
    consts.field_names = ["Індекс", "Константа"]
    for lex, idx in sorted(tableOfConst.items(), key=lambda x: x[1]):
        consts.add_row([idx, lex])
    print('\nТаблиця констант:')
    print(consts)

# Перевірка перед синтаксичним аналізом
if len(tableOfSymb) > 0:
    print('\n' + '=' * 50)
    print('ПОЧАТОК СИНТАКСИЧНОГО АНАЛІЗУ')
    print('=' * 50 + '\n')
    try:
        parseProgram()
    except Exception as e:
        print(f'\nПомилка під час синтаксичного аналізу: {e}')
        import traceback
        traceback.print_exc()
else:
    print('\nСинтаксичний аналіз неможливий — таблиця символів пуста')
    
