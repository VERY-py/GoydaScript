import sys
import os
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from system.compiler import Compiler

def main(file: str = None, debug: str = None):
    if file is None:
        parser = argparse.ArgumentParser(description="Goyda Language Compiler")
        parser.add_argument("file", help="Путь к .gs файлу")
        parser.add_argument("--debug", "-d", nargs='?', const='small', choices=['small', 'full'],
                            help="Режим отладки: small (базовая инфо) или full (подробная)")
        nargs = parser.parse_args()
        args = {'file': nargs.file, 'debug': nargs.debug}
    else:
        args = {'file': file, 'debug': debug}

    try:
        compiler = Compiler(debug=args['debug'])
        compiler.compile(args['file'])
    except KeyboardInterrupt:
        print("\n\n✗ Компиляция прервана пользователем")
        sys.exit(-1)
    except Exception as e:
        print(f"\n✗ Критическая ошибка: {e}")
        if args['debug'] == 'full':
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()