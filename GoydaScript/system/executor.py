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
        self.error_occurred = False
        self.error_message = ""
        self.stop_execution = False  # флаг для немедленной остановки

    def execute(self, statements: list, functions: Dict = None) -> Optional[Any]:
        if functions:
            self.functions = functions

        self.return_value = None
        self.error_occurred = False
        self.error_message = ""
        self.stop_execution = False

        try:
            for stmt in statements:
                if self.stop_execution or self.return_value is not None:
                    break
                self._execute_statement(stmt)
        except KeyboardInterrupt:
            print("\n\n!<>! Прерывание пользователем !<>!")
            return -1
        except Exception as e:
            self.error_occurred = True
            self.error_message = str(e)
            print(f"\n!<>! ОШИБКА ВЫПОЛНЕНИЯ !<>!")
            print(e)
            return 1

        if self.error_occurred:
            return 1
        return self.return_value

    def _execute_statement(self, stmt: Dict):
        if self.stop_execution or self.error_occurred:
            return

        try:
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
            elif stmt['type'] == 'try_except':
                self._execute_try_except(stmt)
        except Exception as e:
            self.error_occurred = True
            self.error_message = str(e)
            self.stop_execution = True
            print(f"\n!!! ОШИБКА: {e}")
            raise  # пробрасываем для немедленной остановки

    def _execute_try_except(self, stmt: Dict):
        """Выполняет блок try-except"""
        if self.stop_execution:
            return

        try:
            # Выполняем блок try
            self._execute_block(stmt['try_block'])
        except Exception as e:
            # Сохраняем текущие переменные
            old_vars = self.variables.copy()

            # Создаем временную переменную с ошибкой
            self.variables[stmt['error_var']] = str(e)

            # Выполняем блок except
            self._execute_block(stmt['except_block'])

            # Удаляем временную переменную и восстанавливаем остальные
            new_vars = self.variables.copy()
            if stmt['error_var'] in new_vars:
                del new_vars[stmt['error_var']]

            # Обновляем переменные, сохраняя изменения из блока except
            for var_name, var_value in new_vars.items():
                if var_name in old_vars:
                    old_vars[var_name] = var_value
                else:
                    old_vars[var_name] = var_value

            self.variables = old_vars

            # Сбрасываем флаг ошибки, так как она обработана
            self.error_occurred = False
            self.stop_execution = False

    def _execute_block(self, block: list):
        for stmt in block:
            if self.stop_execution:
                break
            self._execute_statement(stmt)

    def _evaluate_expression(self, expr: Dict) -> Any:
        if self.stop_execution:
            return None

        if not expr:
            return None

        expr_type = expr['type']

        if expr_type in ['int', 'float', 'str', 'bool']:
            return expr['value']

        elif expr_type == 'variable':
            if expr['name'] not in self.variables:
                raise Exception(f"Переменная '{expr['name']}' не определена")
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
                else:
                    raise Exception(f"Ключ словаря должен быть хешируемым типом, получен {type(key)}")
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
                if right == 0:
                    raise Exception("Деление на ноль")
                return left / right
            elif op == '//':
                if right == 0:
                    raise Exception("Деление на ноль")
                return left // right
            elif op == '%':
                if right == 0:
                    raise Exception("Деление на ноль")
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

    def _execute_function_call(self, stmt: Dict) -> Any:
        """Выполняет вызов функции и возвращает результат"""
        if self.stop_execution:
            return None

        func_name = stmt['name']

        if func_name not in self.functions:
            raise Exception(f"Функция '{func_name}' не определена")

        func = self.functions[func_name]
        args = [self._evaluate_expression(arg) for arg in stmt['args']]

        if len(args) != len(func['params']):
            raise Exception(f"Функция '{func_name}' ожидает {len(func['params'])} аргументов, получено {len(args)}")

        # Сохраняем текущие переменные
        global_vars = self.variables.copy()

        # Создаем локальный контекст
        local_vars = {}
        for param_name, arg_value in zip(func['params'], args):
            local_vars[param_name] = arg_value

        # Добавляем глобальные переменные в локальный контекст (для чтения)
        for var_name, var_value in global_vars.items():
            if var_name not in local_vars:
                local_vars[var_name] = var_value

        self.variables = local_vars

        result = None
        old_return = self.return_value
        self.return_value = None

        try:
            for statement in func['body']:
                if self.stop_execution:
                    break
                self._execute_statement(statement)
                if self.return_value is not None:
                    result = self.return_value
                    break
        except Exception as e:
            # Восстанавливаем переменные перед пробросом ошибки
            self.variables = global_vars
            self.return_value = old_return
            raise e

        # Обновляем глобальные переменные (только если не было ошибки)
        if not self.stop_execution:
            for var_name, var_value in self.variables.items():
                if var_name not in func['params'] and var_name in global_vars:
                    global_vars[var_name] = var_value

        self.variables = global_vars
        self.return_value = old_return

        return result if result is not None else 0

    def _execute_while_loop(self, stmt: Dict):
        """Выполняет цикл while"""
        if self.stop_execution:
            return

        self.loops_found += 1

        max_iterations = 10000
        iterations = 0

        while not self.stop_execution and self._evaluate_expression(stmt['condition']) and iterations < max_iterations:
            iterations += 1
            self._execute_block(stmt['block'])
            if self.return_value is not None:
                break

    def _execute_assign_op(self, stmt: Dict):
        if self.stop_execution:
            return

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
        if self.stop_execution:
            return

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
        if self.stop_execution:
            return

        self.prints_found += 1
        if stmt['value']:
            value = self._evaluate_expression(stmt['value'])
            print(value)
        else:
            print()

    def _execute_return(self, stmt: Dict):
        if self.stop_execution:
            return

        self.returns_found += 1
        if stmt['value']:
            self.return_value = self._evaluate_expression(stmt['value'])
        else:
            self.return_value = None

    def _execute_if_chain(self, stmt: Dict):
        if self.stop_execution:
            return

        self.ifs_found += 1
        executed = False

        for condition in stmt['conditions']:
            if self.stop_execution:
                break

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
        if self.stop_execution:
            return

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
            if self.stop_execution:
                break
            self.variables[stmt['element']] = element_value
            self._execute_block(stmt['block'])
            if self.return_value is not None:
                break