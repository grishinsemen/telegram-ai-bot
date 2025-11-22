# Скрипт для настройки MiniMax MCP в Cursor

Write-Host "=== Настройка MiniMax MCP для Cursor ===" -ForegroundColor Green
Write-Host ""

# Добавляем uv в PATH
$env:Path = "C:\Users\SEMEN\.local\bin;$env:Path"

# Проверяем расположение конфигурации Cursor
$cursorAppData = "$env:APPDATA\Cursor"
$cursorUserData = "$env:APPDATA\Cursor\User"
$cursorGlobalStorage = "$env:APPDATA\Cursor\User\globalStorage"

Write-Host "Поиск директории настроек Cursor..." -ForegroundColor Yellow

# Создаем директории если их нет
if (-not (Test-Path $cursorAppData)) {
    Write-Host "Директория Cursor не найдена. Убедитесь, что Cursor установлен." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $cursorUserData)) {
    New-Item -ItemType Directory -Path $cursorUserData -Force | Out-Null
    Write-Host "Создана директория: $cursorUserData" -ForegroundColor Green
}

if (-not (Test-Path $cursorGlobalStorage)) {
    New-Item -ItemType Directory -Path $cursorGlobalStorage -Force | Out-Null
    Write-Host "Создана директория: $cursorGlobalStorage" -ForegroundColor Green
}

# Путь к конфигурационному файлу MCP
$mcpConfigPath = "$cursorGlobalStorage\mcp.json"

Write-Host ""
Write-Host "Конфигурационный файл: $mcpConfigPath" -ForegroundColor Cyan
Write-Host ""

# Проверяем существующую конфигурацию
$existingConfig = $null
if (Test-Path $mcpConfigPath) {
    Write-Host "Найден существующий файл конфигурации" -ForegroundColor Yellow
    try {
        $existingConfig = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
        Write-Host "Текущая конфигурация загружена" -ForegroundColor Green
    } catch {
        Write-Host "Ошибка при чтении конфигурации. Создам новый файл." -ForegroundColor Yellow
    }
}

# Создаем или обновляем конфигурацию
if ($null -eq $existingConfig -or $null -eq $existingConfig.mcpServers) {
    $config = @{
        mcpServers = @{}
    }
} else {
    $config = $existingConfig
}

# Добавляем или обновляем конфигурацию minimax
$minimaxConfig = @{
    command = "uvx"
    args = @("minimax-mcp")
    env = @{
        MINIMAX_API_KEY = "YOUR_API_KEY_HERE"
    }
}

# Проверяем, нужно ли обновить API ключ
if ($config.mcpServers.PSObject.Properties.Name -contains "minimax") {
    Write-Host "Конфигурация minimax уже существует" -ForegroundColor Yellow
    $currentApiKey = $config.mcpServers.minimax.env.MINIMAX_API_KEY
    if ($currentApiKey -ne "YOUR_API_KEY_HERE" -and -not [string]::IsNullOrWhiteSpace($currentApiKey)) {
        Write-Host "Текущий API ключ уже настроен" -ForegroundColor Green
        $minimaxConfig.env.MINIMAX_API_KEY = $currentApiKey
    } else {
        Write-Host "Требуется настройка API ключа" -ForegroundColor Yellow
    }
} else {
    Write-Host "Добавляю новую конфигурацию minimax" -ForegroundColor Green
}

$config.mcpServers.minimax = $minimaxConfig

# Сохраняем конфигурацию
try {
    $config | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath -Encoding UTF8
    Write-Host ""
    Write-Host "[OK] Конфигурация сохранена: $mcpConfigPath" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Ошибка при сохранении конфигурации: $_" -ForegroundColor Red
    exit 1
}

# Показываем содержимое файла
Write-Host ""
Write-Host "=== Содержимое конфигурации ===" -ForegroundColor Cyan
Get-Content $mcpConfigPath
Write-Host ""

# Проверяем API ключ
if ($config.mcpServers.minimax.env.MINIMAX_API_KEY -eq "YOUR_API_KEY_HERE") {
    Write-Host "[WARNING] ВАЖНО: Замените YOUR_API_KEY_HERE на ваш реальный API ключ MiniMax!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Как получить API ключ:" -ForegroundColor Cyan
    Write-Host "1. Зайдите на https://platform.minimax.io/" -ForegroundColor White
    Write-Host "2. Зарегистрируйтесь или войдите в аккаунт" -ForegroundColor White
    Write-Host "3. Перейдите в раздел API Keys" -ForegroundColor White
    Write-Host "4. Создайте новый ключ и скопируйте его" -ForegroundColor White
    Write-Host "5. Откройте файл: $mcpConfigPath" -ForegroundColor White
    Write-Host "6. Замените YOUR_API_KEY_HERE на ваш ключ" -ForegroundColor White
    Write-Host ""
}

Write-Host "=== Следующие шаги ===" -ForegroundColor Cyan
Write-Host "1. Если API ключ еще не настроен, откройте файл и замените YOUR_API_KEY_HERE" -ForegroundColor White
Write-Host "2. Полностью закройте и перезапустите Cursor IDE" -ForegroundColor White
Write-Host "3. После перезапуска MCP сервер minimax должен автоматически подключиться" -ForegroundColor White
Write-Host "4. Проверьте подключение в настройках Cursor (Settings -> MCP)" -ForegroundColor White
Write-Host ""
















