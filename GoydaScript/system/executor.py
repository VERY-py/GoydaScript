from typing import Dict, Any, Optional

class Executor:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.variables: Dict[str, Any] = {}
        self.return_value: Optional[int] = None
        self.prints_found = 0
        self.returns_found = 0
        self.ifs_found = 0
        self.loops_found = 0

    def execute(self, statements: list) -> Optional[int]:
        self.return_value = None

        for stmt in statements:
            if self.return_value is not None:
                break

            if stmt['type'] == 'decl':
                self._execute_decl(stmt)
            elif stmt['type'] == 'list_decl':
                self._execute_list_decl(stmt)
            elif stmt['type'] == 'for_loop':
                self._execute_for_loop(stmt)
            elif stmt['type'] == 'method_call':
                self._execute_method_call(stmt)
            elif stmt['type'] == 'print':
                self._execute_print(stmt)
            elif stmt['type'] == 'return':
                self._execute_return(stmt)
            elif stmt['type'] == 'if_chain':
                self._execute_if_chain(stmt)
            elif stmt['type'] == 'assign_get':
                self._execute_assign_get(stmt)

        return self.return_value

    def _execute_for_loop(self, stmt: Dict):
        """Выполняет цикл for с поддержкой range и списков"""
        self.loops_found += 1

        # Получаем итератор (список)
        iterator = None

        if stmt['iterator']['type'] == 'list_ref':
            # Ссылка на существующий список
            list_name = stmt['iterator']['value']
            if list_name in self.variables and isinstance(self.variables[list_name], list):
                iterator = self.variables[list_name]
        elif stmt['iterator']['type'] == 'list_literal':
            # Литерал списка
            iterator = stmt['iterator']['value']
        elif stmt['iterator']['type'] == 'range':
            # Range объект - вычисляем значения
            range_data = stmt['iterator']

            if range_data.get('is_constant', False):
                # Константный range
                start = range_data['start']
                end = range_data['end']
                iterator = list(range(start, end))
            else:
                # Range с переменными
                # Определяем start
                if 'start_var' in range_data:
                    var_name = range_data['start_var']
                    if var_name in self.variables and isinstance(self.variables[var_name], int):
                        start = self.variables[var_name]
                    else:
                        start = 0
                else:
                    start = range_data.get('start', 0)

                # Определяем end
                if 'end_var' in range_data:
                    var_name = range_data['end_var']
                    if var_name in self.variables and isinstance(self.variables[var_name], int):
                        end = self.variables[var_name]
                    else:
                        end = 0
                else:
                    end = range_data.get('end', 0)

                iterator = list(range(start, end))

        if not isinstance(iterator, list):
            return

        # Для каждого элемента выполняем блок
        for element_value in iterator:
            # Временно сохраняем элемент в переменную
            self.variables[stmt['element']] = element_value
            self._execute_block(stmt['block'])

            # Если был return, прерываем цикл
            if self.return_value is not None:
                break

    def _execute_list_decl(self, stmt: Dict):
        """Создает новый список из литерала или range"""
        if stmt['source']['type'] == 'literal':
            self.variables[stmt['name']] = stmt['source']['values'].copy()
        elif stmt['source']['type'] == 'range':
            range_data = stmt['source']

            if range_data.get('is_constant', False):
                # Константный range
                start = range_data['start']
                end = range_data['end']
                self.variables[stmt['name']] = list(range(start, end))
            else:
                # Range с переменными
                # Определяем start
                if 'start_var' in range_data:
                    var_name = range_data['start_var']
                    if var_name in self.variables and isinstance(self.variables[var_name], int):
                        start = self.variables[var_name]
                    else:
                        start = 0
                else:
                    start = range_data.get('start', 0)

                # Определяем end
                if 'end_var' in range_data:
                    var_name = range_data['end_var']
                    if var_name in self.variables and isinstance(self.variables[var_name], int):
                        end = self.variables[var_name]
                    else:
                        end = 0
                else:
                    end = range_data.get('end', 0)

                self.variables[stmt['name']] = list(range(start, end))

    def _execute_block(self, block: list):
        """Выполняет блок инструкций"""
        for stmt in block:
            if self.return_value is not None:
                break

            if stmt['type'] == 'assign':
                self.variables[stmt['name']] = stmt['value']
            elif stmt['type'] == 'method_call':
                self._execute_method_call(stmt)
            elif stmt['type'] == 'print':
                self._execute_print(stmt)
            elif stmt['type'] == 'return':
                self._execute_return(stmt)
            elif stmt['type'] == 'for_loop':
                self._execute_for_loop(stmt)

    def _execute_method_call(self, stmt: Dict):
        """Выполняет вызов метода"""
        if stmt['object'] not in self.variables:
            return

        obj = self.variables[stmt['object']]

        if stmt['method'] == 'append':
            if isinstance(obj, list) and len(stmt['args']) > 0:
                obj.append(stmt['args'][0])

        elif stmt['method'] == 'get':
            # get обрабатывается в assign_get
            pass

    def _execute_assign_get(self, stmt: Dict):
        """Выполняет присваивание результата метода get"""
        if stmt['method_call']['object'] not in self.variables:
            return

        obj = self.variables[stmt['method_call']['object']]
        args = stmt['method_call']['args']

        if isinstance(obj, list) and len(args) > 0:
            index = args[0]
            if 0 <= index < len(obj):
                self.variables[stmt['name']] = obj[index]

    def _execute_decl(self, stmt: Dict):
        """Выполняет объявление переменной"""
        if stmt['is_input']:
            prompt = stmt['prompt']
            if prompt:
                value = input(prompt + " ")
            else:
                value = input("Ввод: ")
            try:
                value = int(value)
            except:
                value = 0
            self.variables[stmt['name']] = value
        else:
            self.variables[stmt['name']] = stmt['value']

    def _execute_print(self, stmt: Dict):
        """Выполняет print"""
        self.prints_found += 1
        if stmt['var'] in self.variables:
            print(self.variables[stmt['var']])
        else:
            print(0)

    def _execute_return(self, stmt: Dict):
        """Выполняет return"""
        self.returns_found += 1
        self.return_value = stmt['value']

    def _execute_if_chain(self, stmt: Dict):
        """Выполняет цепочку if/else if/else"""
        self.ifs_found += 1
        executed = False

        for condition in stmt['conditions']:
            if condition['type'] in ['if', 'else_if']:
                if not executed and self._check_condition(condition['condition']):
                    self._execute_block(condition['block'])
                    executed = True
            elif condition['type'] == 'else' and not executed:
                self._execute_block(condition['block'])
                executed = True

    def _check_condition(self, condition: Dict) -> bool:
        """Проверяет условие"""
        if condition['left'] in self.variables:
            return self.variables[condition['left']] == condition['right']
        return False