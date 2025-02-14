from typing import List, Union, Optional, Dict

# Тип для токенов линейного представления
Token = Dict[str, Union[str, int]] 

# Тип для дерева AST
ASTNode = Union[Dict[str, Union[str, int, 'ASTNode']], None]

# Функция для токенизации: преобразование рег выражения в список токенов.
def tokenize(regex: str) -> List[Token]:
    tokens = []
    i = 0
    while i < len(regex):  
        if regex[i] in {'|', '(', ')', '?', ':', '*', '='}: # Проверка на специальные символы
            tokens.append({'type': 'Operator', 'value': regex[i]})
            i += 1
        elif regex[i].isalpha() or regex[i].isdigit():  
            tokens.append({'type': 'Symbol', 'value': regex[i]})
            i += 1
        else:
            raise ValueError(f"Недопустимый символ: {regex[i]}")
    tokens.append({'type': 'EndOfString', 'value': '$'})
    return tokens

# Парсер преобразует рег выражение в дерево AST (абстрактное синтаксическое дерево)
def parse(regex: str) -> ASTNode:
    tokens = tokenize(regex)  
    pos = 0
    group_count = 0 # Счётчик групп
    lookahead_depth = 0  # Ограничение глубины lookahead

    print("Типы операторов и токенов:")
    for token in tokens:
        print(token)
    print()

    #  Текущий токен
    def current_token() -> Token:
        nonlocal pos
        return tokens[pos] if pos < len(tokens) else {'type': 'EndOfString', 'value': '$'}

    # Переход к следующему токену
    def consume(expected: Optional[str] = None):
        nonlocal pos
        token = current_token()
        if expected and token['value'] != expected:
            raise ValueError(f"Ожидался {expected}, но получен {token['value']}")  
        pos += 1

    # Парсинг альтернативы и возврат узла Alternation
    def parse_alternative() -> ASTNode:
        node = parse_concatenation()
        while current_token()['value'] == '|':
            consume('|')
            right = parse_concatenation()
            node = {'type': 'Alternation', 'left': node, 'right': right}
        return node

    # Парсинг конкатенации и возврат узла Concatenation
    def parse_concatenation() -> ASTNode:
        node = parse_iteration()
        while current_token()['value'] not in {'|', ')', '$'}:
            right = parse_iteration()
            node = {'type': 'Concatenation', 'left': node, 'right': right}
        return node

    # Парсинг повторения (*) и возврат узла Iteration
    def parse_iteration() -> ASTNode:
        node = parse_low()
        while current_token()['value'] == '*':
            consume('*')
            node = {'type': 'Iteration', 'node': node}
        return node

    # Парсинг групп, символов и специальных модификаторов
    def parse_low() -> ASTNode:
        nonlocal group_count, lookahead_depth
        token = current_token()
        if token['value'] == '(':
            consume('(')
            if current_token()['value'] == '?':
                consume('?')
                if current_token()['value'] == ':':
                    consume(':')
                    node = parse_alternative()
                    consume(')')
                    return {'type': 'NoCapture', 'node': node}
                elif current_token()['value'] == '=':
                    if lookahead_depth > 0:
                        raise ValueError("Запрещено вложение опережающих проверок")
                    consume('=')
                    lookahead_depth += 1
                    node = parse_alternative()
                    lookahead_depth -= 1
                    consume(')')

                    # Проверка: есть ли группы захвата внутри lookahead
                    def contains_capture(node):
                        if not node:
                            return False
                        if node['type'] == 'Capture':
                            return True
                        return any(contains_capture(node.get(k)) for k in ['left', 'right', 'node'])

                    if contains_capture(node):
                        raise ValueError("Группы захвата недопустимы внутри опережающих проверок")

                    return {'type': 'LookAhead', 'node': node}
                elif current_token()['value'].isdigit():  # Ссылка на группу
                    group_index = int(current_token()['value'])
                    consume()
                    consume(')')
                    return {'type': 'GroupLink', 'group_index': group_index}
            else:
                group_count += 1
                group_index = group_count
                print(f"{{'type': 'CaptureStart', 'index': {group_index}}}")
                node = parse_alternative()
                consume(')')
                print(f"{{'type': 'CaptureEnd', 'index': {group_index}}}")
                return {'type': 'Capture', 'node': node, 'index': group_index}
        elif token['type'] == 'Symbol':
            val = token['value']
            consume()
            return {'type': 'Symbol', 'val': val}
        else:
            raise ValueError(f"Недопустимый токен: {current_token()}")
    
    node = parse_alternative()
    if current_token()['value'] != '$':
        raise ValueError("Ожидался конец выражения")
    if group_count > 9: # Ограничение на количество групп захвата !
        raise ValueError("Количество групп захвата не должно превышать 9")
    return node

# Функция для печати дерева 
def print_tree(node: ASTNode, indent: str = "", is_last: bool = False, is_root: bool = True):
    if node is None:
        return
    branch = "" if is_root else ("└── " if is_last else "├── ")  
    next_indent = "" if is_root else ("    " if is_last else "│   ")

    # Улучшенный вывод дерева 
    if node['type'] == 'Symbol':
        print(f"{indent}{branch}{node['type']} ({node['val']})")  # Отображение символа
    elif node['type'] == 'GroupLink':
        print(f"{indent}{branch}{node['type']} (#{node['group_index']})")  # Отображение номера группы
    else:
        print(f"{indent}{branch}{node['type']}")
        
    for key in ['left', 'right', 'node']:
        if key in node:
            print_tree(node[key], indent + next_indent, key == 'right', False)

# Функция для построения КС-грамматики
def build_ks_grammar(regex: str) -> str:
    ast = parse(regex)
    rules = []
    counter = 1
    
    def traverse(node, parent_name="S"):
        nonlocal counter
        if node is None:
            return ""
        
        if node['type'] == 'Symbol':
            rule_name = f"T_{counter}"
            counter += 1
            rules.insert(0, f"{rule_name} = {node['val']}")
            return rule_name
        elif node['type'] in {'Concatenation', 'Alternation'}:
            left_name = traverse(node['left'], parent_name)
            right_name = traverse(node['right'], parent_name)
            rule_name = f"N_{counter}"
            counter += 1
            sep = '|' if node['type'] == 'Alternation' else ''
            rules.insert(0, f"{rule_name} = {left_name} {sep} {right_name}")
            return rule_name
        elif node['type'] == 'Iteration':
            sub_name = traverse(node['node'], parent_name)
            rule_name = f"N_{counter}"
            counter += 1
            rules.insert(0, f"{rule_name} = {sub_name} {rule_name} | ε")
            return rule_name
        elif node['type'] in {'Capture', 'NoCapture'}:
            return traverse(node['node'], parent_name)
        return ""
    
    start_symbol = traverse(ast)
    rules.append(f"S = {start_symbol} | ε")
    return "\n".join(reversed(rules))

regex_examples = [
    # "(?=abc)def",   # Правильный lookahead
    # "(?=(?=abc)def)", # Неправильный вложенный lookahead
    # "(a|(bb))(a|(?3))", # Корректная ссылка на группу
    # "a*b",   
    # "(a|b)c", 
    # "(ab)*c",
    "(?=(a))(?:a)", # Группы захвата недопустимы внутри опережающей проверки
    "(?=(a))a" # Группы захвата недопустимы внутри опережающей проверки
]

for regex in regex_examples:
    print(f"\nПроверка: {regex}")
    ast = parse(regex)
    print("\nРегулярное выражение корректно.")
    print("\nДерево AST:")
    print_tree(ast)
    print(f"\nГрамматика для {regex}:")
    print(build_ks_grammar(regex))

