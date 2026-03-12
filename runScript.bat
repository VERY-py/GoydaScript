@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ========================================
echo     Запуск компилятора GoydaScript
echo ========================================
echo.

set /p script_name=Введите название скрипта: 

if "!script_name!"=="" (
    echo Ошибка: Имя скрипта не может быть пустым!
    pause
    exit /b 1
)

echo.
echo Выберите режим отладки:
echo  [n] - Нет
echo  [s] - Маленькая (small)
echo  [f] - Полная (full)
echo.

set /p debug_mode=Ваш выбор (n/s/f): 

set debug_param=

if /i "!debug_mode!"=="s" (
    set debug_param=-d small
    echo Выбран режим: Маленькая отладка
) else if /i "!debug_mode!"=="f" (
    set debug_param=-d full
    echo Выбран режим: Полная отладка
) else if /i "!debug_mode!"=="n" (
    set debug_param=
    echo Выбран режим: Без отладки
) else (
    echo Неверный выбор! Используется режим без отладки.
    set debug_param=
)

echo.
echo Запуск: python GoydaScript/goyda2py.py !script_name! !debug_param!
echo.

python GoydaScript/goyda2py.py %script_name% %debug_param%

echo.
pause