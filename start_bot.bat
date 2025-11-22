@echo off
chcp 65001 >nul
echo ========================================
echo   Запуск Telegram бота
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python и добавьте его в PATH
    pause
    exit /b 1
)

REM Проверяем наличие файла бота
if not exist "telegram_bot.py" (
    echo ОШИБКА: Файл telegram_bot.py не найден!
    echo Убедитесь, что вы запускаете батник из правильной папки
    pause
    exit /b 1
)

REM Проверяем наличие конфига
if not exist "telegram_config.json" (
    echo ОШИБКА: Файл telegram_config.json не найден!
    echo Создайте файл конфигурации перед запуском бота
    pause
    exit /b 1
)

echo Запуск бота...
echo.

python telegram_bot.py

if errorlevel 1 (
    echo.
    echo Ошибка при запуске бота!
    echo Проверьте настройки в telegram_config.json
    pause
)







