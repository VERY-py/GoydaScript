from typing import Dict, Any, Optional
from system.tokens import Token, TokenType

class Parser:
    """Парсит токены и подготавливает AST для выполнения"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.variables: Dict[str, Any] = {}
        self.statements = []  # Здесь будем хранить AST
        self.error_occurred = False
        self.error_message = ""

    def parse(self, tokens: list[Token]) -> list:
        self.statements = []
        self.pos = 0
        self.tokens = tokens

        try:
            while self.pos < len(self.tokens):
                token = self.tokens[self.pos]

                if token.type == TokenType.INT:
                    stmt = self._parse_decl_stmt()
                    if stmt:
                        self.statements.append(stmt)
                elif token.type == TokenType.LIST:
                    stmt = self._parse_list_decl()
                    if stmt:
                        self.statements.append(stmt)
                elif token.type == TokenType.FOR:
                    stmt = self._parse_for_loop()
                    if stmt:
                        self.statements.append(stmt)
                elif token.type == TokenType.PRINT:
                    stmt = self._parse_print_stmt()
                    if stmt:
                        self.statements.append(stmt)
                elif token.type == TokenType.RETURN:
                    stmt = self._parse_return_stmt()
                    if stmt:
                        self.statements.append(stmt)
                elif token.type == TokenType.IF:
                    stmt = self._parse_if_stmt()
                    if stmt:
                        self.statements.append(stmt)
                else:
                    method_call = self._parse_method_call()
                    if method_call:
                        self.statements.append(method_call)
                    else:
                        self.pos += 1

            return self.statements

        except Exception as e:
            self.error_occurred = True
            self.error_message = f"Ошибка парсинга: {str(e)}"
            return []

    def _parse_expression(self) -> Optional[Dict]:
        """Парсит выражение (может быть число, переменная, range, список)"""
        if self.pos >= len(self.tokens):
            return None

        token = self.tokens[self.pos]

        if token.type == TokenType.NUMBER:
            value = int(token.value)
            self.pos += 1
            return {'type': 'number', 'value': value}

        elif token.type == TokenType.ID:
            name = token.value
            self.pos += 1
            return {'type': 'variable', 'name': name}

        elif token.type == TokenType.RANGE:
            return self._parse_range()

        elif token.type == TokenType.LBRACKET:
            values = self._parse_list_literal()
            if values is not None:
                return {'type': 'list_literal', 'values': values}

        return None

    def _parse_range(self) -> Optional[Dict]:
        """Парсит range(5), range(0, 10) или range(a), range(0, a)"""
        self.pos += 1  # пропускаем range

        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.LPAREN:
            self.error_occurred = True
            self.error_message = "Ожидалась '(' после range"
            return None

        self.pos += 1  # пропускаем (

        args = []

        # Парсим аргументы
        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RPAREN:
            if self.tokens[self.pos].type == TokenType.NUMBER:
                args.append(int(self.tokens[self.pos].value))
                self.pos += 1
            elif self.tokens[self.pos].type == TokenType.ID:
                # Поддержка переменных
                args.append(self.tokens[self.pos].value)
                self.pos += 1
            elif self.tokens[self.pos].type == TokenType.COMMA:
                self.pos += 1
            else:
                self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
            self.pos += 1

        # Создаем range объект с единой структурой
        if len(args) == 1:
            if isinstance(args[0], int):
                # range(5) - константа
                return {
                    'type': 'range',
                    'start': 0,
                    'end': args[0],
                    'is_constant': True
                }
            else:
                # range(a) - переменная
                return {
                    'type': 'range',
                    'start': 0,
                    'end_var': args[0],  # имя переменной
                    'is_constant': False
                }
        elif len(args) == 2:
            if isinstance(args[0], int) and isinstance(args[1], int):
                # range(0, 5) - обе константы
                return {
                    'type': 'range',
                    'start': args[0],
                    'end': args[1],
                    'is_constant': True
                }
            elif isinstance(args[0], int) and isinstance(args[1], str):
                # range(0, a) - старт константа, конец переменная
                return {
                    'type': 'range',
                    'start': args[0],
                    'end_var': args[1],
                    'is_constant': False
                }
            elif isinstance(args[0], str) and isinstance(args[1], int):
                # range(a, 5) - старт переменная, конец константа
                return {
                    'type': 'range',
                    'start_var': args[0],
                    'end': args[1],
                    'is_constant': False
                }
            else:
                # range(a, b) - обе переменные
                return {
                    'type': 'range',
                    'start_var': args[0],
                    'end_var': args[1],
                    'is_constant': False
                }
        else:
            self.error_occurred = True
            self.error_message = "range() требует 1 или 2 аргумента"
            return None

    def _parse_decl_stmt(self) -> Optional[Dict]:
        """Парсит объявление переменной в AST"""
        self.pos += 1  # int

        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.ID:
            self.error_occurred = True
            self.error_message = "Ожидался идентификатор после int"
            return None

        var_name = self.tokens[self.pos].value
        self.pos += 1

        stmt = {
            'type': 'decl',
            'name': var_name,
            'value': None,
            'is_input': False,
            'prompt': ''
        }

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.ASSIGN:
            self.pos += 1

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.INPUT:
                stmt['is_input'] = True
                self.pos += 1

                if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.LPAREN:
                    self.pos += 1

                if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.STRING:
                    stmt['prompt'] = self.tokens[self.pos].value
                    self.pos += 1

                if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
                    self.pos += 1

            elif self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.NUMBER:
                stmt['value'] = int(self.tokens[self.pos].value)
                self.pos += 1

        self._skip_to_semi()
        return stmt

    def _parse_list_decl(self) -> Optional[Dict]:
        """Парсит объявление списка: list l = [10, 5, 2] или list l = range(5)"""
        self.pos += 1  # list

        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.ID:
            self.error_occurred = True
            self.error_message = "Ожидался идентификатор после list"
            return None

        var_name = self.tokens[self.pos].value
        self.pos += 1

        stmt = {
            'type': 'list_decl',
            'name': var_name,
            'source': None  # может быть список значений или range
        }

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.ASSIGN:
            self.pos += 1

            if self.pos < len(self.tokens):
                if self.tokens[self.pos].type == TokenType.LBRACKET:
                    # Литерал списка [1, 2, 3]
                    values = self._parse_list_literal()
                    if values is not None:
                        stmt['source'] = {
                            'type': 'literal',
                            'values': values
                        }
                elif self.tokens[self.pos].type == TokenType.RANGE:
                    # range(5)
                    range_obj = self._parse_range()
                    if range_obj:
                        stmt['source'] = range_obj

        self._skip_to_semi()
        return stmt

    def _parse_for_loop(self) -> Optional[Dict]:
        """Парсит цикл for: for a in l { ... } или for a in range(5) { ... }"""
        self.pos += 1  # for

        stmt = {
            'type': 'for_loop',
            'element': None,
            'iterator': None,  # будет словарь с единой структурой
            'block': []
        }

        # Получаем элемент
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.ID:
            stmt['element'] = self.tokens[self.pos].value
            self.pos += 1

        # Проверяем 'in'
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.IN:
            self.pos += 1

        # Проверяем, что идет после 'in'
        if self.pos < len(self.tokens):
            if self.tokens[self.pos].type == TokenType.ID:
                # Это ссылка на список
                stmt['iterator'] = {
                    'type': 'list_ref',
                    'value': self.tokens[self.pos].value,
                    'values': list()
                } or None
                self.pos += 1
            elif self.tokens[self.pos].type == TokenType.RANGE:
                # Это range()
                range_obj = self._parse_range()
                if range_obj:
                    stmt['iterator'] = range_obj
            elif self.tokens[self.pos].type == TokenType.LBRACKET:
                # Это литерал списка [1, 2, 3]
                list_values = self._parse_list_literal()
                if list_values is not None:
                    stmt['iterator'] = {
                        'type': 'list_literal',
                        'value': list_values,
                        'values': list_values  # Дублируем для совместимости
                    }

        # Парсим блок
        stmt['block'] = self._parse_block()

        return stmt

    def _parse_list_literal(self) -> Optional[list]:
        """Парсит [1, 2, 3] и возвращает список значений"""
        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.LBRACKET:
            return None

        self.pos += 1

        values = []

        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RBRACKET:
            if self.tokens[self.pos].type == TokenType.NUMBER:
                values.append(int(self.tokens[self.pos].value))
                self.pos += 1
            elif self.tokens[self.pos].type == TokenType.COMMA:
                self.pos += 1
            else:
                self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RBRACKET:
            self.pos += 1

        return values

    def _parse_method_call(self) -> Optional[Dict]:
        """Парсит вызов метода: list.append(5) или list.get(1)"""
        if self.pos + 3 >= len(self.tokens):
            return None

        if (self.tokens[self.pos].type == TokenType.ID and
                self.tokens[self.pos + 1].type == TokenType.DOT and
                self.tokens[self.pos + 2].type == TokenType.ID and
                self.tokens[self.pos + 3].type == TokenType.LPAREN):

            obj_name = self.tokens[self.pos].value
            method_name = self.tokens[self.pos + 2].value
            self.pos += 4

            args = []

            if self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RPAREN:
                if self.tokens[self.pos].type == TokenType.NUMBER:
                    args.append(int(self.tokens[self.pos].value))
                    self.pos += 1
                elif self.tokens[self.pos].type == TokenType.ID:
                    args.append(self.tokens[self.pos].value)
                    self.pos += 1

            while self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.COMMA:
                self.pos += 1

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
                self.pos += 1

            return {
                'type': 'method_call',
                'object': obj_name,
                'method': method_name,
                'args': args
            }

        return None

    def _parse_print_stmt(self) -> Optional[Dict]:
        """Парсит print в AST"""
        self.pos += 1  # print

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.LPAREN:
            self.pos += 1

        stmt = {'type': 'print', 'var': None}

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.ID:
            stmt['var'] = self.tokens[self.pos].value
            self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
            self.pos += 1

        self._skip_to_semi()
        return stmt

    def _parse_return_stmt(self) -> Optional[Dict]:
        """Парсит return в AST"""
        self.pos += 1  # return

        stmt = {'type': 'return', 'value': None}

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.NUMBER:
            stmt['value'] = int(self.tokens[self.pos].value)
            self.pos += 1

        self._skip_to_semi()
        return stmt

    def _parse_if_stmt(self) -> Optional[Dict]:
        """Парсит if/else if/else в AST"""
        stmt = {
            'type': 'if_chain',
            'conditions': []
        }

        while self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]

            if current_token.type == TokenType.IF:
                self.pos += 1
                condition = self._parse_condition()
                block = self._parse_block()
                stmt['conditions'].append({
                    'type': 'if',
                    'condition': condition,
                    'block': block
                })

            elif current_token.type == TokenType.ELSE:
                self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.IF:
                    # else if
                    self.pos += 1
                    condition = self._parse_condition()
                    block = self._parse_block()
                    stmt['conditions'].append({
                        'type': 'else_if',
                        'condition': condition,
                        'block': block
                    })
                else:
                    # else
                    block = self._parse_block()
                    stmt['conditions'].append({
                        'type': 'else',
                        'block': block
                    })
                    break  # else завершает цепочку
            else:
                break

        return stmt

    def _parse_condition(self) -> Optional[Dict]:
        """Парсит условие"""
        if (self.pos + 2 < len(self.tokens) and
                self.tokens[self.pos].type == TokenType.ID and
                self.tokens[self.pos + 1].type == TokenType.EQEQ and
                self.tokens[self.pos + 2].type == TokenType.NUMBER):
            condition = {
                'left': self.tokens[self.pos].value,
                'op': '==',
                'right': int(self.tokens[self.pos + 2].value)
            }
            self.pos += 3
            return condition
        return None

    def _parse_block(self) -> list:
        """Парсит блок кода в AST"""
        # Пропускаем до {
        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.LBRACE:
            self.pos += 1

        if self.pos < len(self.tokens):
            self.pos += 1  # пропускаем {

        block_statements = []

        # Парсим инструкции внутри блока
        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RBRACE:
            token = self.tokens[self.pos]

            if token.type == TokenType.ID:
                # Может быть присваивание или вызов метода
                if self.pos + 1 < len(self.tokens):
                    if self.tokens[self.pos + 1].type == TokenType.ASSIGN:
                        # Присваивание
                        var_name = token.value
                        self.pos += 2
                        # Проверяем, может это результат метода get
                        method_call = self._parse_method_call()
                        if method_call and method_call['method'] == 'get':
                            # Это присваивание результата get
                            block_statements.append({
                                'type': 'assign_get',
                                'name': var_name,
                                'method_call': method_call
                            })
                        elif self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.NUMBER:
                            block_statements.append({
                                'type': 'assign',
                                'name': var_name,
                                'value': int(self.tokens[self.pos].value)
                            })
                            self.pos += 1
                    else:
                        # Возможно вызов метода без присваивания
                        method_call = self._parse_method_call()
                        if method_call:
                            block_statements.append(method_call)
                        else:
                            self.pos += 1
                else:
                    self.pos += 1

            elif token.type == TokenType.PRINT:
                stmt = self._parse_print_stmt()
                if stmt:
                    block_statements.append(stmt)
                continue

            elif token.type == TokenType.RETURN:
                stmt = self._parse_return_stmt()
                if stmt:
                    block_statements.append(stmt)
                continue

            elif token.type == TokenType.FOR:
                stmt = self._parse_for_loop()
                if stmt:
                    block_statements.append(stmt)
                continue

            else:
                self.pos += 1

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.SEMI:
                self.pos += 1

        # Пропускаем }
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RBRACE:
            self.pos += 1

        return block_statements

    def _skip_to_semi(self):
        while (self.pos < len(self.tokens) and
               self.tokens[self.pos].type != TokenType.SEMI):
            self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.SEMI:
            self.pos += 1
