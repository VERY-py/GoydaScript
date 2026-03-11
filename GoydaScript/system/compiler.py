import os, sys, time
from typing import Optional
from system.lexer import Lexer
from system.parser import Parser
from system.executor import Executor

class Compiler:
    def __init__(self, debug: Optional[str] = None):
        self.debug = debug  # None, 'small' или 'full'
        self.start_time = time.time()
        self.lexer_time = 0
        self.parser_time = 0
        self.executor_time = 0

    def _load_file(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            raise ValueError(f"Файл '{filepath}' не найден")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def compile(self, filepath: str):
        # Показываем только в full debug
        if self.debug == 'full':
            print("🚀 Запуск компилятора GoydaScript...")
            print("═" * 60)

        # Этап 1: Загрузка файла
        if self.debug == 'full':
            print("📖 Загрузка файла...")

        code = self._load_file(filepath)

        if self.debug == 'full':
            print(f"✅ Файл загружен ({len(code)} символов)\n")

        # Этап 2: Лексический анализ
        if self.debug == 'full':
            print("🔍 Лексический анализ...")

        start = time.time()
        lexer = Lexer(code)
        tokens = lexer.get_tokens()
        self.lexer_time = time.time() - start

        if self.debug == 'full':
            print(f"✅ Найдено токенов: {len(tokens)}\n")

        # Этап 3: Парсинг (компиляция в AST)
        if self.debug == 'full':
            print("🏗️  Компиляция в AST...")

        start = time.time()
        parser = Parser(debug=self.debug == 'full')
        ast = parser.parse(tokens)
        self.parser_time = time.time() - start

        if parser.error_occurred:
            print(f"❌ Ошибка компиляции: {parser.error_message}")
            sys.exit(1)

        if self.debug == 'full':
            print(f"✅ AST построено (узлов: {len(ast)})\n")

        # Этап 4: Выполнение программы
        # Для small debug показываем заголовок
        if self.debug == 'small':
            print("📋 ВЫВОД ПРОГРАММЫ:")
            print("─" * 40)
        elif self.debug == 'full':
            print("═" * 60)
            print("🚀 ВЫПОЛНЕНИЕ ПРОГРАММЫ")
            print("═" * 60 + "\n")

        start = time.time()
        executor = Executor(debug=self.debug == 'full')
        return_value = executor.execute(ast)
        self.executor_time = time.time() - start

        # Для small debug добавляем разделитель после вывода
        if self.debug == 'small':
            print("─" * 40)
        elif self.debug == 'full':
            print("\n" + "═" * 60)
            print("✅ ВЫПОЛНЕНИЕ ЗАВЕРШЕНО")
            print("═" * 60 + "\n")

        total_time = time.time() - self.start_time
        self._show_results(executor, tokens, ast, total_time, return_value)

    def _show_results(self, executor: Executor, tokens: list, ast: list, total_time: float,
                      return_value: Optional[int]):
        exit_code = return_value if return_value is not None else 0

        # Всегда показываем exit code
        print(f"✓ Exit code: {exit_code}")

        # Для debug режимов показываем дополнительную информацию
        if self.debug == 'small':
            print(f"⏱️  Время: {total_time:.3f}с | Токенов: {len(tokens)} | {len(tokens) / total_time:.0f} ток/с")

        elif self.debug == 'full':
            print("\n" + "═" * 60)
            print("📊 ОТЧЕТ О КОМПИЛЯЦИИ")
            print("═" * 60)
            print(f"⏱️   Общее время:       {total_time:.3f}с")
            print(f"📦  Токенов:           {len(tokens)}")
            print(f"🌳  Узлов AST:         {len(ast)}")
            print(f"⚡  Скорость:          {len(tokens) / total_time:.0f} токенов/с")
            print(f"📈 Этапы:")
            print(f"   Лексический анализ: {self.lexer_time:.3f}с ({self.lexer_time / total_time * 100:.1f}%)")
            print(f"   Парсинг (AST):      {self.parser_time:.3f}с ({self.parser_time / total_time * 100:.1f}%)")
            print(f"   Выполнение:         {self.executor_time:.3f}с ({self.executor_time / total_time * 100:.1f}%)")

            print(f"\n🔍 DEBUG ИНФО:")
            print(f"   Переменные:         {list(executor.variables.keys())}")
            print(f"   Вызовов print:      {executor.prints_found}")
            print(f"   Найдено return:     {executor.returns_found}")
            print(f"   Найдено условий:    {executor.ifs_found}")
            print(f"   Циклов:             {executor.loops_found}")
            print("═" * 60)

        sys.exit(exit_code)
