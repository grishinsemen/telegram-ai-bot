@echo off
chcp 65001 >nul
echo ========================================
echo   Запуск Telegram бота в фоновом режиме
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

echo Запуск бота в фоновом режиме...
start "Telegram Bot" /min python telegram_bot.py
echo.
echo Бот запущен в фоновом окне.
echo Чтобы остановить бота, закройте окно "Telegram Bot" или найдите процесс python.exe в диспетчере задач.
echo.
pause







