@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ========================================
echo     Запуск транслятора GoydaScript
echo ========================================
echo.

:: Запрос имени скрипта
set /p script_name=Введите название скрипта: 

:: Проверка, что имя скрипта не пустое
if "!script_name!"=="" (
    echo Ошибка: Имя скрипта не может быть пустым!
    pause
    exit /b 1
)

:: Запрос режима отладки
echo.
echo Выберите режим отладки:
echo  [n] - Нет
echo  [s] - Маленькая (small)
echo  [f] - Полная (full)
echo.

set /p debug_mode=Ваш выбор (n/s/f): 

:: Установка параметра отладки
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

:: Запуск Python скрипта
python GoydaScript/goyda2py.py %script_name% %debug_param%

:: Проверка результата выполнения
if errorlevel 1 (
    echo.
    echo Ошибка при выполнении скрипта!
) else (
    echo.
    echo Скрипт успешно выполнен!
)

echo.
pause