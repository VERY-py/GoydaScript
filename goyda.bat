@echo off
chcp 65001 >nul

setlocal

if "%1"=="" (
    echo Ошибка: Имя скрипта не может быть пустым!
    goto :show_help
)

set SCRIPT_NAME=%1
shift

set DEBUG_PARAM=

:parse_args
if "%1"=="" goto :run

if "%1"=="-h" (
    goto :show_help
)
if "%1"=="--help" (
    goto :show_help
)
if "%1"=="-dsmall" (
    set DEBUG_PARAM=-d small
    shift
    goto :parse_args
)
if "%1"=="-dfull" (
    set DEBUG_PARAM=-d full
    shift
    goto :parse_args
)

echo Неизвестная опция: %1
goto :show_help

:run
if defined DEBUG_PARAM (
    python GoydaScript/gs2py.py %SCRIPT_NAME% %DEBUG_PARAM%
) else (
    python GoydaScript/gs2py.py %SCRIPT_NAME%
)
goto :eof

:show_help
echo Использование: goyda ^<имя_скрипта^> [ОПЦИИ]
echo.
echo Опции:
echo   -h, --help       Показать эту справку
echo   -dsmall         Малый режим отладки (-d small)
echo   -dfull         Полный режим отладки (-d full)
echo.
echo Примеры:
echo   goyda myscript.gs              # без отладки
echo   goyda myscript.gs -dsmall       # малый режим отладки
echo   goyda myscript.gs -dfull       # полный режим отладки
goto :eof