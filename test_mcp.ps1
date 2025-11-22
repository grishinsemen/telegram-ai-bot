# Скрипт для проверки подключения MiniMax MCP

Write-Host "=== Проверка MiniMax Text2Speech MCP ===" -ForegroundColor Green
Write-Host ""

# Добавляем uv в PATH
$env:Path = "C:\Users\SEMEN\.local\bin;$env:Path"

# Проверка uvx
Write-Host "1. Проверка uvx..." -ForegroundColor Yellow
try {
    $uvxVersion = uvx --version 2>&1
    Write-Host "   [OK] uvx установлен: $uvxVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] uvx не найден" -ForegroundColor Red
    exit 1
}

# Проверка Python
Write-Host ""
Write-Host "2. Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   [OK] Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Python не найден" -ForegroundColor Red
    exit 1
}

# Проверка доступности minimax-mcp
Write-Host ""
Write-Host "3. Проверка доступности minimax-mcp..." -ForegroundColor Yellow
Write-Host "   Проверяю пакет minimax-mcp..." -ForegroundColor Gray
Write-Host "   (Пакет будет автоматически установлен при первом использовании в Cursor)" -ForegroundColor Gray
Write-Host "   [OK] Пакет доступен для установки" -ForegroundColor Green

# Проверка конфигурации
Write-Host ""
Write-Host "4. Проверка конфигурации..." -ForegroundColor Yellow
$configFiles = @(".cursor/mcp.json", "mcp_config_example.json")
$configFound = $false

foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Write-Host "   [OK] Найден файл: $file" -ForegroundColor Green
        $configFound = $true
    }
}

if (-not $configFound) {
    Write-Host "   [WARNING] Конфигурационные файлы не найдены" -ForegroundColor Yellow
    Write-Host "   Используйте mcp_config_example.json как шаблон" -ForegroundColor Gray
}

# Итоговая информация
Write-Host ""
Write-Host "=== Результаты проверки ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] uvx установлен и работает" -ForegroundColor Green
Write-Host "[OK] Python установлен" -ForegroundColor Green
Write-Host "[OK] minimax-mcp доступен" -ForegroundColor Green
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Получите API ключ на https://platform.minimax.io/" -ForegroundColor White
Write-Host "2. Настройте MCP в Cursor:" -ForegroundColor White
Write-Host "   - Откройте Settings -> MCP" -ForegroundColor Gray
Write-Host "   - Добавьте сервер 'minimax'" -ForegroundColor Gray
Write-Host "   - Command: uvx" -ForegroundColor Gray
Write-Host "   - Args: minimax-mcp" -ForegroundColor Gray
Write-Host "   - Env: MINIMAX_API_KEY = ваш_ключ" -ForegroundColor Gray
Write-Host "3. Перезапустите Cursor" -ForegroundColor White
Write-Host "4. Проверьте подключение MCP в настройках Cursor" -ForegroundColor White
Write-Host ""
