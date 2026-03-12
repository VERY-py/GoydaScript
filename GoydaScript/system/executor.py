from typing import Dict, Any, Optional


class Executor:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Dict] = {}
        self.return_value: Optional[Any] = None
        self.prints_found = 0
        self.returns_found = 0
        self.ifs_found = 0
        self.loops_found = 0
        self.call_stack = []

    def execute(self, statements: list, functions: Dict = None) -> Optional[Any]:
        if functions:
            self.functions = functions

        self.return_value = None
        self.call_stack = [{'vars': self.variables.copy()}]

        for stmt in statements:
            if self.return_value is not None:
                break
            self._execute_statement(stmt)

        return self.return_value

    def _execute_statement(self, stmt: Dict):
        if stmt['type'] == 'decl':
            self._execute_decl(stmt)
        elif stmt['type'] == 'for_loop':
            self._execute_for_loop(stmt)
        elif stmt['type'] == 'while_loop':
            self._execute_while_loop(stmt)
        elif stmt['type'] == 'function_call':
            self._execute_function_call(stmt)
        elif stmt['type'] == 'print':
            self._execute_print(stmt)
        elif stmt['type'] == 'return':
            self._execute_return(stmt)
        elif stmt['type'] == 'if_chain':
            self._execute_if_chain(stmt)
        elif stmt['type'] == 'assign_op':
            self._execute_assign_op(stmt)

    def _execute_function_call(self, stmt: Dict) -> Any:
        """Выполняет вызов функции и возвращает результат"""
        func_name = stmt['name']

        if func_name not in self.functions:
            raise Exception(f"Функция '{func_name}' не определена")

        func = self.functions[func_name]
        args = [self._evaluate_expression(arg) for arg in stmt['args']]

        if len(args) != len(func['params']):
            raise Exception(f"Функция '{func_name}' ожидает {len(func['params'])} аргументов, получено {len(args)}")

        old_vars = self.variables.copy()
        old_return = self.return_value

        self.variables = {}
        for param_name, arg_value in zip(func['params'], args):
            self.variables[param_name] = arg_value

        result = None
        self.return_value = None

        for statement in func['body']:
            self._execute_statement(statement)
            if self.return_value is not None:
                result = self.return_value
                break

        self.variables = old_vars
        self.return_value = old_return

        return result if result is not None else 0

    def _execute_while_loop(self, stmt: Dict):
        """Выполняет цикл while"""
        self.loops_found += 1

        max_iterations = 10000
        iterations = 0

        while self._evaluate_expression(stmt['condition']) and iterations < max_iterations:
            iterations += 1
            self._execute_block(stmt['block'])
            if self.return_value is not None:
                break

    def _evaluate_expression(self, expr: Dict) -> Any:
        if not expr:
            return None

        expr_type = expr['type']

        if expr_type in ['int', 'float', 'str', 'bool']:
            return expr['value']

        elif expr_type == 'variable':
            return self.variables.get(expr['name'], None)

        elif expr_type == 'function_call':
            return self._execute_function_call(expr)

        elif expr_type == 'list_literal':
            return [self._evaluate_expression(e) for e in expr['elements']]

        elif expr_type == 'dict_literal':
            result = {}
            for pair in expr['pairs']:
                key = self._evaluate_expression(pair['key'])
                value = self._evaluate_expression(pair['value'])
                if isinstance(key, (int, float, str, bool, tuple)):
                    result[key] = value
            return result

        elif expr_type == 'range':
            args = [self._evaluate_expression(arg) for arg in expr['args']]
            if len(args) == 1:
                return list(range(int(args[0])))
            else:
                return list(range(int(args[0]), int(args[1])))

        elif expr_type == 'unary_op':
            value = self._evaluate_expression(expr['expr'])
            if expr['op'] == 'not':
                return not value
            elif expr['op'] == '-':
                return -value

        elif expr_type == 'binary_op':
            left = self._evaluate_expression(expr['left'])
            right = self._evaluate_expression(expr['right'])
            op = expr['op']

            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
            elif op == '//':
                return left // right
            elif op == '%':
                return left % right
            elif op == '**':
                return left ** right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '>':
                return left > right
            elif op == '<':
                return left < right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right
            elif op == 'is':
                return left is right
            elif op == 'and':
                return left and right
            elif op == 'or':
                return left or right

        return None

    def _execute_block(self, block: list):
        for stmt in block:
            if self.return_value is not None:
                break
            self._execute_statement(stmt)

    def _execute_assign_op(self, stmt: Dict):
        if stmt['name'] not in self.variables:
            self.variables[stmt['name']] = 0

        current = self.variables[stmt['name']]
        value = self._evaluate_expression(stmt['value'])
        op = stmt['op']

        if op == '=':
            self.variables[stmt['name']] = value
        elif op == '+=':
            self.variables[stmt['name']] = current + value
        elif op == '-=':
            self.variables[stmt['name']] = current - value
        elif op == '*=':
            self.variables[stmt['name']] = current * value
        elif op == '/=':
            self.variables[stmt['name']] = current / value
        elif op == '//=':
            self.variables[stmt['name']] = current // value
        elif op == '%=':
            self.variables[stmt['name']] = current % value
        elif op == '**=':
            self.variables[stmt['name']] = current ** value

    def _execute_decl(self, stmt: Dict):
        if stmt['is_input']:
            prompt = stmt['prompt']
            value = input(prompt + " ") if prompt else input("Ввод: ")

            if stmt['var_type'] == 'int':
                try:
                    value = int(value)
                except:
                    value = 0
            elif stmt['var_type'] == 'float':
                try:
                    value = float(value)
                except:
                    value = 0.0
            elif stmt['var_type'] == 'bool':
                value = value.lower() in ['true', '1', 'yes', 'да']
            else:
                value = str(value)

            self.variables[stmt['name']] = value
        else:
            value = self._evaluate_expression(stmt['value']) if stmt['value'] else None
            self.variables[stmt['name']] = value

    def _execute_print(self, stmt: Dict):
        self.prints_found += 1
        if stmt['value']:
            value = self._evaluate_expression(stmt['value'])
            print(value)
        else:
            print()

    def _execute_return(self, stmt: Dict):
        """Выполняет return"""
        self.returns_found += 1
        if stmt['value']:
            self.return_value = self._evaluate_expression(stmt['value'])
        else:
            self.return_value = None

    def _execute_if_chain(self, stmt: Dict):
        self.ifs_found += 1
        executed = False

        for condition in stmt['conditions']:
            if condition['type'] in ['if', 'else_if']:
                if not executed:
                    cond_value = self._evaluate_expression(condition['condition'])
                    if cond_value:
                        self._execute_block(condition['block'])
                        executed = True
            elif condition['type'] == 'else' and not executed:
                self._execute_block(condition['block'])
                executed = True

    def _execute_for_loop(self, stmt: Dict):
        self.loops_found += 1

        iterator = None
        if stmt['iterator']['type'] == 'iter_ref':
            list_name = stmt['iterator']['value']
            if list_name in self.variables:
                iterator = self.variables[list_name]
        else:
            iterator = self._evaluate_expression(stmt['iterator'])

        if not isinstance(iterator, (list, tuple, range)):
            return

        for element_value in iterator:
            self.variables[stmt['element']] = element_value
            self._execute_block(stmt['block'])
            if self.return_value is not None:
                break