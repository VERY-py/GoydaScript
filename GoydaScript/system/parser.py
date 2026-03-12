from typing import Dict, Optional
from .tokens import Token, TokenType

class Parser:
    def __init__(self, debug: str = None):
        self.debug = debug
        self.functions: Dict[str, Dict] = {}
        self.statements = []
        self.error_occurred = False
        self.error_message = ""

    def parse(self, tokens: list[Token]) -> list:
        if self.debug == 'full':
            print("=== ТОКЕНЫ ===")
            for i, t in enumerate(tokens[:20]):
                print(f"{i}: {t.type} = '{t.value}'")

        self.statements = []
        self.functions = {}
        self.pos = 0
        self.tokens = tokens
        main_body = []

        try:
            while self.pos < len(self.tokens):
                if self.tokens[self.pos].type == TokenType.FUNC:
                    if (self.pos + 1 < len(self.tokens) and
                            self.tokens[self.pos + 1].type == TokenType.MAIN):
                        self.pos += 2

                        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.LPAREN:
                            while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RPAREN:
                                self.pos += 1
                            self.pos += 1

                        main_body = self._parse_block()
                        break
                    else:
                        func_def = self._parse_function_definition()
                        if func_def:
                            self.functions[func_def['name']] = func_def
                else:
                    self.pos += 1

            if not main_body:
                self.error_occurred = True
                self.error_message = "Функция main не найдена"
                return []

            return main_body

        except Exception as e:
            self.error_occurred = True
            self.error_message = f"Ошибка парсинга: {str(e)}"
            return []

    def _parse_function_definition(self) -> Optional[Dict]:
        """Парсит определение функции: func name(params) { body }"""
        if self.debug == 'full':
            print(f"DEBUG: парсим функцию на позиции {self.pos}, токен: {self.tokens[self.pos].type}")
        start_pos = self.pos
        self.pos += 1

        if self.pos >= len(self.tokens):
            self.error_occurred = True
            self.error_message = "Неожиданный конец файла после func"
            return None

        if self.tokens[self.pos].type not in [TokenType.ID, TokenType.MAIN]:
            print(f"DEBUG: ошибка - ожидался ID или MAIN, но получен {self.tokens[self.pos].type}")
            self.error_occurred = True
            self.error_message = "Ожидалось имя функции после func"
            return None

        func_name = self.tokens[self.pos].value
        self.pos += 1

        params = []
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.LPAREN:
            self.pos += 1
            while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RPAREN:
                if self.tokens[self.pos].type == TokenType.ID:
                    params.append(self.tokens[self.pos].value)
                    self.pos += 1
                elif self.tokens[self.pos].type == TokenType.COMMA:
                    self.pos += 1
                else:
                    self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
                self.pos += 1

        body = self._parse_block()

        return {
            'name': func_name,
            'params': params,
            'body': body,
            'start': start_pos,
            'end': self.pos
        }

    def _parse_expression(self, precedence: int = 0) -> Optional[Dict]:
        return self._parse_binary_expression(precedence)

    def _parse_binary_expression(self, min_precedence: int = 0) -> Optional[Dict]:
        left = self._parse_unary_expression()
        if not left:
            return None

        precedence = {
            'or': 1,
            'and': 2,
            'is': 3, 'is_not': 3,
            '==': 4, '!=': 4, '>': 4, '<': 4, '>=': 4, '<=': 4,
            '+': 5, '-': 5,
            '*': 6, '/': 6, '//': 6, '%': 6,
            '**': 7
        }

        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            op_type = None
            if token.type in [TokenType.AND, TokenType.OR, TokenType.IS]:
                op_type = token.type.value.lower()
            elif token.type == TokenType.NEQ:
                op_type = '!='
            elif token.type == TokenType.GT:
                op_type = '>'
            elif token.type == TokenType.LT:
                op_type = '<'
            elif token.type == TokenType.GTE:
                op_type = '>='
            elif token.type == TokenType.LTE:
                op_type = '<='
            elif token.type == TokenType.EQEQ:
                op_type = '=='
            elif token.type == TokenType.PLUS:
                op_type = '+'
            elif token.type == TokenType.MINUS:
                op_type = '-'
            elif token.type == TokenType.MULT:
                op_type = '*'
            elif token.type == TokenType.DIV:
                op_type = '/'
            elif token.type == TokenType.FLOORDIV:
                op_type = '//'
            elif token.type == TokenType.MOD:
                op_type = '%'
            elif token.type == TokenType.POW:
                op_type = '**'

            if not op_type or op_type not in precedence:
                break

            current_precedence = precedence[op_type]

            if op_type == '**':
                if current_precedence < min_precedence:
                    break
            else:
                if current_precedence <= min_precedence:
                    break

            self.pos += 1
            right = self._parse_binary_expression(current_precedence + (1 if op_type != '**' else 0))
            if not right:
                self.error_occurred = True
                self.error_message = f"Ожидалось выражение после оператора {op_type}"
                return None

            left = {
                'type': 'binary_op',
                'op': op_type,
                'left': left,
                'right': right
            }

        return left

    def _parse_unary_expression(self) -> Optional[Dict]:
        token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

        if token and token.type == TokenType.NOT:
            self.pos += 1
            expr = self._parse_unary_expression()
            return {
                'type': 'unary_op',
                'op': 'not',
                'expr': expr
            }

        if token and token.type == TokenType.MINUS:
            self.pos += 1
            expr = self._parse_unary_expression()
            return {
                'type': 'unary_op',
                'op': '-',
                'expr': expr
            }

        return self._parse_call_expression()

    def _parse_call_expression(self) -> Optional[Dict]:
        """Парсит вызов функции: name(args)"""
        if self.pos >= len(self.tokens):
            return None

        if (self.tokens[self.pos].type == TokenType.ID and
                self.pos + 1 < len(self.tokens) and
                self.tokens[self.pos + 1].type == TokenType.LPAREN):

            func_name = self.tokens[self.pos].value
            self.pos += 2

            args = []
            while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RPAREN:
                expr = self._parse_expression()
                if expr:
                    args.append(expr)
                elif self.tokens[self.pos].type == TokenType.COMMA:
                    self.pos += 1
                else:
                    self.pos += 1

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
                self.pos += 1

            return {
                'type': 'function_call',
                'name': func_name,
                'args': args
            }

        return self._parse_primary_expression()

    def _parse_primary_expression(self) -> Optional[Dict]:
        if self.pos >= len(self.tokens):
            return None

        token = self.tokens[self.pos]

        if token.type == TokenType.NUMBER:
            value = int(token.value)
            self.pos += 1
            return {'type': 'int', 'value': value}

        elif token.type == TokenType.FLOAT_NUMBER:
            value = float(token.value)
            self.pos += 1
            return {'type': 'float', 'value': value}

        elif token.type == TokenType.STRING:
            value = token.value
            self.pos += 1
            return {'type': 'str', 'value': value}

        elif token.type == TokenType.TRUE:
            self.pos += 1
            return {'type': 'bool', 'value': True}

        elif token.type == TokenType.FALSE:
            self.pos += 1
            return {'type': 'bool', 'value': False}

        elif token.type == TokenType.ID:
            name = token.value
            self.pos += 1
            return {'type': 'variable', 'name': name}

        elif token.type == TokenType.LPAREN:
            self.pos += 1
            expr = self._parse_expression()
            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
                self.pos += 1
            return expr

        elif token.type == TokenType.LBRACKET:
            return self._parse_list_literal()

        elif token.type == TokenType.LBRACE:
            return self._parse_dict_literal()

        elif token.type == TokenType.RANGE:
            return self._parse_range()

        return None

    def _parse_range(self) -> Optional[Dict]:
        self.pos += 1

        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.LPAREN:
            self.error_occurred = True
            self.error_message = "Ожидалась '(' после range"
            return None

        self.pos += 1
        args = []

        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RPAREN:
            expr = self._parse_expression()
            if expr:
                args.append(expr)
            elif self.tokens[self.pos].type == TokenType.COMMA:
                self.pos += 1
            else:
                self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
            self.pos += 1

        if 1 <= len(args) <= 2:
            return {'type': 'range', 'args': args}
        else:
            self.error_occurred = True
            self.error_message = "range() требует 1 или 2 аргумента"
            return None

    def _parse_list_literal(self) -> Optional[Dict]:
        self.pos += 1
        elements = []

        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RBRACKET:
            expr = self._parse_expression()
            if expr:
                elements.append(expr)
            elif self.tokens[self.pos].type == TokenType.COMMA:
                self.pos += 1
            else:
                self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RBRACKET:
            self.pos += 1

        return {'type': 'list_literal', 'elements': elements}

    def _parse_dict_literal(self) -> Optional[Dict]:
        self.pos += 1
        pairs = []

        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RBRACE:
            key = self._parse_expression()
            if not key:
                self.pos += 1
                continue

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.COLON:
                self.pos += 1
            else:
                self.error_occurred = True
                self.error_message = "Ожидалось ':' после ключа словаря"
                return None

            value = self._parse_expression()
            if value:
                pairs.append({'key': key, 'value': value})

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.COMMA:
                self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RBRACE:
            self.pos += 1

        return {'type': 'dict_literal', 'pairs': pairs}

    def _parse_decl_stmt(self, type_token: TokenType) -> Optional[Dict]:
        type_map = {
            TokenType.INT: 'int',
            TokenType.FLOAT: 'float',
            TokenType.STR: 'str',
            TokenType.BOOL: 'bool',
            TokenType.LIST: 'list',
            TokenType.TUPLE: 'tuple',
            TokenType.DICT: 'dict'
        }

        var_type = type_map[type_token]
        self.pos += 1

        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.ID:
            self.error_occurred = True
            self.error_message = f"Ожидался идентификатор после {var_type}"
            return None

        var_name = self.tokens[self.pos].value
        self.pos += 1

        stmt = {
            'type': 'decl',
            'var_type': var_type,
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

            else:
                expr = self._parse_expression()
                if expr:
                    stmt['value'] = expr

        self._skip_to_semi()
        return stmt

    def _parse_while_loop(self) -> Optional[Dict]:
        """Парсит цикл while: while condition { block }"""
        self.pos += 1

        condition = self._parse_expression()
        if not condition:
            self.error_occurred = True
            self.error_message = "Ожидалось условие после while"
            return None

        block = self._parse_block()

        return {
            'type': 'while_loop',
            'condition': condition,
            'block': block
        }

    def _parse_for_loop(self) -> Optional[Dict]:
        self.pos += 1

        stmt = {
            'type': 'for_loop',
            'element': None,
            'iterator': None,
            'block': []
        }

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.ID:
            stmt['element'] = self.tokens[self.pos].value
            self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.IN:
            self.pos += 1

        if self.pos < len(self.tokens):
            if self.tokens[self.pos].type == TokenType.ID:
                stmt['iterator'] = {
                    'type': 'iter_ref',
                    'value': self.tokens[self.pos].value
                }
                self.pos += 1
            else:
                expr = self._parse_expression()
                if expr:
                    stmt['iterator'] = expr

        stmt['block'] = self._parse_block()
        return stmt

    def _parse_print_stmt(self) -> Optional[Dict]:
        self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.LPAREN:
            self.pos += 1

        stmt = {'type': 'print', 'value': None}
        expr = self._parse_expression()
        if expr:
            stmt['value'] = expr

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RPAREN:
            self.pos += 1

        self._skip_to_semi()
        return stmt

    def _parse_return_stmt(self) -> Optional[Dict]:
        self.pos += 1
        stmt = {'type': 'return', 'value': None}
        expr = self._parse_expression()
        if expr:
            stmt['value'] = expr
        self._skip_to_semi()
        return stmt

    def _parse_if_stmt(self) -> Optional[Dict]:
        stmt = {'type': 'if_chain', 'conditions': []}

        while self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]

            if current_token.type == TokenType.IF:
                self.pos += 1
                condition = self._parse_expression()
                block = self._parse_block()
                stmt['conditions'].append({
                    'type': 'if',
                    'condition': condition,
                    'block': block
                })

            elif current_token.type == TokenType.ELSE:
                self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.IF:
                    self.pos += 1
                    condition = self._parse_expression()
                    block = self._parse_block()
                    stmt['conditions'].append({
                        'type': 'else_if',
                        'condition': condition,
                        'block': block
                    })
                else:
                    block = self._parse_block()
                    stmt['conditions'].append({'type': 'else', 'block': block})
                    break
            else:
                break

        return stmt

    def _parse_block(self) -> list:
        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.LBRACE:
            self.pos += 1

        if self.pos < len(self.tokens):
            self.pos += 1

        block_statements = []

        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.RBRACE:
            token = self.tokens[self.pos]

            if token.type in [TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL,
                              TokenType.LIST, TokenType.TUPLE, TokenType.DICT]:
                stmt = self._parse_decl_stmt(token.type)
                if stmt:
                    block_statements.append(stmt)
                continue

            elif token.type == TokenType.WHILE:
                stmt = self._parse_while_loop()
                if stmt:
                    block_statements.append(stmt)
                continue

            elif token.type == TokenType.ID:
                if self.pos + 1 < len(self.tokens):
                    next_token = self.tokens[self.pos + 1]
                    assign_ops = {
                        TokenType.ASSIGN: '=',
                        TokenType.PLUS_ASSIGN: '+=',
                        TokenType.MINUS_ASSIGN: '-=',
                        TokenType.MULT_ASSIGN: '*=',
                        TokenType.DIV_ASSIGN: '/=',
                        TokenType.FLOORDIV_ASSIGN: '//=',
                        TokenType.MOD_ASSIGN: '%=',
                        TokenType.POW_ASSIGN: '**='
                    }

                    if next_token.type in assign_ops:
                        var_name = token.value
                        op = assign_ops[next_token.type]
                        self.pos += 2
                        expr = self._parse_expression()
                        if expr:
                            block_statements.append({
                                'type': 'assign_op',
                                'name': var_name,
                                'op': op,
                                'value': expr
                            })
                        continue

                call_expr = self._parse_call_expression()
                if call_expr and call_expr['type'] == 'function_call':
                    block_statements.append(call_expr)
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

            elif token.type == TokenType.IF:
                stmt = self._parse_if_stmt()
                if stmt:
                    block_statements.append(stmt)
                continue

            else:
                self.pos += 1

            if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.SEMI:
                self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.RBRACE:
            self.pos += 1

        return block_statements

    def _skip_to_semi(self):
        while (self.pos < len(self.tokens) and
               self.tokens[self.pos].type != TokenType.SEMI):
            self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos].type == TokenType.SEMI:
            self.pos += 1