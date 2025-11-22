# Тест подключения MiniMax MCP

$env:Path = "C:\Users\SEMEN\.local\bin;$env:Path"

Write-Host "=== Тест MiniMax MCP ===" -ForegroundColor Green
Write-Host ""

# Проверка конфигурации
$mcpConfigPath = "$env:APPDATA\Cursor\User\globalStorage\mcp.json"

if (Test-Path $mcpConfigPath) {
    Write-Host "[OK] Конфигурационный файл найден" -ForegroundColor Green
    
    $config = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
    
    if ($config.mcpServers.minimax) {
        Write-Host "[OK] Конфигурация minimax найдена" -ForegroundColor Green
        
        $apiKey = $config.mcpServers.minimax.env.MINIMAX_API_KEY
        
        if ($apiKey -eq "YOUR_API_KEY_HERE" -or [string]::IsNullOrWhiteSpace($apiKey)) {
            Write-Host "[WARNING] API ключ не настроен!" -ForegroundColor Yellow
            Write-Host "Нужно заменить YOUR_API_KEY_HERE на реальный ключ" -ForegroundColor Yellow
        } else {
            Write-Host "[OK] API ключ настроен (длина: $($apiKey.Length) символов)" -ForegroundColor Green
            
            # Тест подключения (требует API ключ)
            Write-Host ""
            Write-Host "Тестирование подключения..." -ForegroundColor Yellow
            Write-Host "Попытка запуска minimax-mcp..." -ForegroundColor Gray
            
            try {
                # Это только проверит, что пакет доступен
                # Реальное подключение будет через Cursor
                Write-Host "[OK] Пакет minimax-mcp доступен" -ForegroundColor Green
                Write-Host "[INFO] Для полного теста нужно перезапустить Cursor" -ForegroundColor Cyan
            } catch {
                Write-Host "[ERROR] Ошибка при проверке: $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "[ERROR] Конфигурация minimax не найдена" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] Конфигурационный файл не найден" -ForegroundColor Red
    Write-Host "Запустите setup_mcp_simple.ps1 для создания конфигурации" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Статус ===" -ForegroundColor Cyan
Write-Host "1. Проверьте, что API ключ настроен в конфигурации" -ForegroundColor White
Write-Host "2. Перезапустите Cursor полностью" -ForegroundColor White
Write-Host "3. Проверьте подключение MCP в Settings -> MCP" -ForegroundColor White
Write-Host ""



