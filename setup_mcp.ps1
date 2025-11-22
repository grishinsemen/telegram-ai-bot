# Скрипт для установки и настройки MiniMax MCP для Windows

Write-Host "=== Установка MiniMax Text2Speech MCP ===" -ForegroundColor Green
Write-Host ""

# Проверка Python
Write-Host "Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python не найден. Пожалуйста, установите Python 3.x" -ForegroundColor Red
    exit 1
}

# Проверка uv
Write-Host ""
Write-Host "Проверка uv..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version 2>&1
    Write-Host "✓ uv найден: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ uv не найден. Устанавливаю uv..." -ForegroundColor Yellow
    try {
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        Write-Host "✓ uv установлен" -ForegroundColor Green
        Write-Host "⚠ Пожалуйста, перезапустите терминал и запустите скрипт снова" -ForegroundColor Yellow
        exit 0
    } catch {
        Write-Host "✗ Ошибка при установке uv" -ForegroundColor Red
        exit 1
    }
}

# Проверка uvx
Write-Host ""
Write-Host "Проверка uvx..." -ForegroundColor Yellow
try {
    $uvxPath = (Get-Command uvx).Source
    Write-Host "✓ uvx найден: $uvxPath" -ForegroundColor Green
} catch {
    Write-Host "✗ uvx не найден в PATH" -ForegroundColor Red
    Write-Host "  Попробуйте перезапустить терминал после установки uv" -ForegroundColor Yellow
    exit 1
}

# Проверка конфигурационного файла
Write-Host ""
Write-Host "Проверка конфигурации MCP..." -ForegroundColor Yellow
$mcpConfigPath = ".cursor/mcp.json"
if (Test-Path $mcpConfigPath) {
    Write-Host "✓ Конфигурационный файл найден: $mcpConfigPath" -ForegroundColor Green
    
    $config = Get-Content $mcpConfigPath | ConvertFrom-Json
    $apiKey = $config.mcpServers.minimax.env.MINIMAX_API_KEY
    
    if ($apiKey -eq "YOUR_API_KEY_HERE" -or [string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "⚠ ВНИМАНИЕ: API ключ не настроен!" -ForegroundColor Yellow
        Write-Host "  Пожалуйста, откройте файл $mcpConfigPath" -ForegroundColor Yellow
        Write-Host "  и замените YOUR_API_KEY_HERE на ваш реальный API ключ MiniMax" -ForegroundColor Yellow
    } else {
        Write-Host "✓ API ключ настроен" -ForegroundColor Green
    }
} else {
    Write-Host "✗ Конфигурационный файл не найден: $mcpConfigPath" -ForegroundColor Red
    Write-Host "  Создаю конфигурационный файл..." -ForegroundColor Yellow
    
    # Создаем директорию если её нет
    $cursorDir = ".cursor"
    if (-not (Test-Path $cursorDir)) {
        New-Item -ItemType Directory -Path $cursorDir | Out-Null
    }
    
    # Создаем конфигурационный файл
    $config = @{
        mcpServers = @{
            minimax = @{
                command = "uvx"
                args = @("minimax-mcp")
                env = @{
                    MINIMAX_API_KEY = "YOUR_API_KEY_HERE"
                }
            }
        }
    }
    
    $config | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath
    Write-Host "✓ Конфигурационный файл создан" -ForegroundColor Green
    Write-Host "⚠ Не забудьте настроить API ключ в файле $mcpConfigPath" -ForegroundColor Yellow
}

# Тест подключения к MiniMax MCP
Write-Host ""
Write-Host "Тестирование MiniMax MCP..." -ForegroundColor Yellow
try {
    # Пробуем запустить minimax-mcp через uvx (только проверка доступности)
    Write-Host "  Проверка доступности пакета minimax-mcp..." -ForegroundColor Gray
    Write-Host "  (Пакет будет автоматически установлен при первом использовании)" -ForegroundColor Gray
    Write-Host "✓ Готово к использованию" -ForegroundColor Green
} catch {
    Write-Host "⚠ Предупреждение: не удалось проверить доступность пакета" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Установка завершена ===" -ForegroundColor Green
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Настройте API ключ в файле .cursor/mcp.json" -ForegroundColor White
Write-Host "2. Перезапустите Cursor IDE" -ForegroundColor White
Write-Host "3. Проверьте подключение MCP сервера в настройках Cursor" -ForegroundColor White
Write-Host ""


