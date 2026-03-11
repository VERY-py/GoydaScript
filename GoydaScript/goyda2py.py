import sys
import argparse
from system.compiler import Compiler

class ProgressBar:
    """Простая шкала прогресса"""

    def __init__(self, total: int, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0

    def update(self, current: int):
        self.current = min(current, self.total)
        percent = (self.current / self.total) * 100
        filled = int(self.width * self.current // self.total)
        bar = '█' * filled + '░' * (self.width - filled)
        sys.stdout.write(f'\r[{bar}] {percent:6.1f}% ({self.current}/{self.total})')
        sys.stdout.flush()

    def finish(self, eta: float):
        self.update(self.total)
        print(f'\r[{'█' * self.width}] 100.0% ✓ (ETA: {eta:.2f}s)')


def main():
    parser = argparse.ArgumentParser(description="Goyda Language Compiler")
    parser.add_argument("file", help="Путь к .goyda файлу")
    parser.add_argument("--debug", "-d", nargs='?', const='small', choices=['small', 'full'],
                        help="Режим отладки: small (базовая инфо) или full (подробная)")
    args = parser.parse_args()

    try:
        compiler = Compiler(debug=args.debug)
        compiler.compile(args.file)
    except KeyboardInterrupt:
        print("\n\n⛔ Компиляция прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()