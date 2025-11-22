# Настройка MiniMax Text2Speech MCP для Cursor

Это руководство поможет вам подключить MiniMax Text2Speech MCP к Cursor IDE.

## Предварительные требования

1. **Python 3.x** - должен быть установлен в системе
2. **uv** - менеджер пакетов Python (для получения `uvx`)
3. **API ключ MiniMax** - получите его на [платформе MiniMax](https://platform.minimax.io/)

## Шаг 1: Установка uv

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

После установки перезапустите терминал или обновите переменные окружения.

### Проверка установки
```powershell
# Windows
(Get-Command uvx).source

# macOS / Linux
which uvx
```

## Шаг 2: Настройка конфигурации MCP

### Вариант A: Через настройки Cursor (рекомендуется)

1. Откройте Cursor IDE
2. Перейдите в настройки (Settings) - обычно через `Ctrl+,` или `File > Preferences > Settings`
3. Найдите раздел "MCP" или "Model Context Protocol"
4. Добавьте новую конфигурацию сервера:
   - Нажмите "Add MCP Server" или аналогичную кнопку
   - Введите имя: `minimax`
   - Command: `uvx`
   - Args: `minimax-mcp`
   - Environment Variables: добавьте `MINIMAX_API_KEY` со значением вашего API ключа

### Вариант B: Через конфигурационный файл

1. Скопируйте содержимое файла `mcp_config_example.json` из этого проекта
2. В Cursor откройте настройки MCP (обычно через Command Palette: `Ctrl+Shift+P` → "MCP Settings")
3. Вставьте конфигурацию или укажите путь к файлу
4. Замените `YOUR_API_KEY_HERE` на ваш реальный API ключ MiniMax

**Примечание**: Расположение конфигурационного файла MCP в Cursor может отличаться в зависимости от версии. Обычно это:
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp.json` или в настройках через UI
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- Linux: `~/.config/Cursor/User/globalStorage/mcp.json`

## Шаг 3: Перезапуск Cursor

После настройки конфигурации:
1. Сохраните все изменения
2. Полностью закройте и перезапустите Cursor IDE
3. MCP сервер MiniMax должен автоматически подключиться при первом запуске

## Проверка подключения

После перезапуска Cursor:
1. Откройте панель MCP в Cursor (обычно в настройках или через команды)
2. Убедитесь, что сервер `minimax` отображается как подключенный
3. Проверьте доступность инструмента `text_to_audio`

## Использование Text2Speech

После успешного подключения вы сможете использовать функцию преобразования текста в речь через MCP инструменты в Cursor.

### Пример использования через MCP:

Инструмент `text_to_audio` принимает следующие параметры:
- `text` - текст для преобразования в речь
- `voice_id` (опционально) - ID голоса (по умолчанию используется системный голос)
- `speed` (опционально) - скорость речи (по умолчанию 1.0)
- `volume` (опционально) - громкость (по умолчанию 1.0)
- `pitch` (опционально) - высота тона (по умолчанию 0)

## Альтернативный вариант: JavaScript версия

Если вы предпочитаете использовать JavaScript версию:

```json
{
  "mcpServers": {
    "minimax": {
      "command": "npx",
      "args": [
        "-y",
        "minimax-mcp-js"
      ],
      "env": {
        "MINIMAX_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

## Устранение неполадок

### Проблема: uvx не найден
**Решение**: Убедитесь, что uv установлен и добавлен в PATH. Перезапустите терминал после установки.

### Проблема: MCP сервер не подключается
**Решение**: 
- Проверьте правильность API ключа
- Убедитесь, что файл `.cursor/mcp.json` находится в корне проекта
- Проверьте логи Cursor на наличие ошибок

### Проблема: Ошибка при выполнении команды
**Решение**: Убедитесь, что Python 3.x установлен и доступен в PATH:
```powershell
python --version
```

## Дополнительные ресурсы

- [Официальная документация MiniMax MCP](https://platform.minimax.io/docs/guides/mcp-guide)
- [MiniMax API Документация](https://platform.minimax.io/docs)
- [Репозиторий uv](https://github.com/astral-sh/uv)

