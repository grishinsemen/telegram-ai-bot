# Быстрый старт: MiniMax Text2Speech MCP

## Автоматическая установка (Windows)

Запустите скрипт установки:
```powershell
.\setup_mcp.ps1
```

Скрипт проверит все зависимости и создаст необходимые файлы.

## Ручная установка

### 1. Установите uv
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Настройте MCP в Cursor

1. Откройте Cursor → Settings → MCP
2. Добавьте новый сервер:
   - **Name**: `minimax`
   - **Command**: `uvx`
   - **Args**: `minimax-mcp`
   - **Environment**: `MINIMAX_API_KEY` = `ваш_api_ключ`

### 3. Перезапустите Cursor

После перезапуска MiniMax MCP будет доступен через инструмент `text_to_audio`.

## Получение API ключа

1. Зарегистрируйтесь на [platform.minimax.io](https://platform.minimax.io/)
2. Перейдите в раздел API Keys
3. Создайте новый ключ и скопируйте его

---

Подробная инструкция: см. [README_MCP_SETUP.md](README_MCP_SETUP.md)


