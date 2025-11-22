#!/usr/bin/env python3
"""
Скрипт для отображения API ключа MiniMax
"""

import json
import os
import sys

def get_api_key():
    """Получает API ключ из различных источников"""
    # 1. Проверяем переменную окружения
    api_key = os.getenv('MINIMAX_API_KEY')
    source = "переменная окружения MINIMAX_API_KEY"
    
    if not api_key:
        # 2. Проверяем конфигурацию Cursor MCP
        config_path = os.path.expandvars(
            r'%APPDATA%\Cursor\User\globalStorage\mcp.json'
        )
        
        if os.path.exists(config_path):
            try:
                for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
                    try:
                        with open(config_path, 'r', encoding=encoding) as f:
                            config = json.load(f)
                            api_key = config.get('mcpServers', {}).get('minimax', {}).get('env', {}).get('MINIMAX_API_KEY')
                            if api_key:
                                source = f"файл конфигурации Cursor: {config_path}"
                                break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
            except Exception as e:
                print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
    
    return api_key, source

def main():
    print("=" * 60)
    print("API КЛЮЧ MINIMAX")
    print("=" * 60)
    print()
    
    api_key, source = get_api_key()
    
    if api_key:
        print(f"Источник: {source}")
        print()
        print("API ключ:")
        print("-" * 60)
        
        # Показываем первые и последние символы для безопасности
        if len(api_key) > 50:
            masked = api_key[:20] + "..." + api_key[-20:]
            print(f"Скрытый вид: {masked}")
            print()
            print("Полный ключ:")
            print(api_key)
        else:
            print(api_key)
        
        print("-" * 60)
        print()
        print("Расположение файла конфигурации:")
        config_path = os.path.expandvars(
            r'%APPDATA%\Cursor\User\globalStorage\mcp.json'
        )
        print(config_path)
        print()
        print("Быстрый доступ:")
        print("Win+R -> %APPDATA%\\Cursor\\User\\globalStorage\\mcp.json")
    else:
        print("API ключ не найден!")
        print()
        print("Проверьте:")
        print("1. Переменную окружения MINIMAX_API_KEY")
        print("2. Файл конфигурации Cursor MCP")
        print()
        print("Расположение конфигурации:")
        config_path = os.path.expandvars(
            r'%APPDATA%\Cursor\User\globalStorage\mcp.json'
        )
        print(config_path)
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()


