#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения chat_id группы в Telegram
1. Добавьте бота в группу
2. Дайте боту права администратора (или хотя бы право отправлять сообщения)
3. Напишите в группе любое сообщение (например, /start)
4. Запустите этот скрипт: python get_telegram_chat_id.py
5. Скрипт покажет все чаты, куда бот может отправлять сообщения
"""

import json
import sys
import os
import requests
import io

# Устанавливаем UTF-8 для вывода в Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_telegram_config():
    """Получает конфигурацию Telegram"""
    config_file = "telegram_config.json"
    if not os.path.exists(config_file):
        print(f"Файл {config_file} не найден", file=sys.stderr)
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
        return None

def get_updates(bot_token):
    """Получает последние обновления от бота"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при запросе к Telegram API: {e}", file=sys.stderr)
        return None

def main():
    config = get_telegram_config()
    if not config:
        sys.exit(1)
    
    bot_token = config.get('bot_token')
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("Ошибка: bot_token не настроен в telegram_config.json", file=sys.stderr)
        sys.exit(1)
    
    print("Получаю информацию о чатах...", file=sys.stderr)
    print("Убедитесь, что:", file=sys.stderr)
    print("1. Бот добавлен в группу", file=sys.stderr)
    print("2. В группе написано хотя бы одно сообщение", file=sys.stderr)
    print("3. Бот имеет права на отправку сообщений", file=sys.stderr)
    print()
    
    updates = get_updates(bot_token)
    if not updates or not updates.get('ok'):
        print(f"Ошибка: {updates.get('description', 'Неизвестная ошибка') if updates else 'Не удалось получить обновления'}", file=sys.stderr)
        sys.exit(1)
    
    chats = {}
    
    for update in updates.get('result', []):
        if 'message' in update:
            msg = update['message']
            chat = msg.get('chat', {})
            chat_id = chat.get('id')
            chat_type = chat.get('type')  # 'private', 'group', 'supergroup', 'channel'
            chat_title = chat.get('title') or chat.get('first_name', 'Без названия')
            
            if chat_id:
                if chat_id not in chats:
                    chats[chat_id] = {
                        'id': chat_id,
                        'type': chat_type,
                        'title': chat_title,
                        'username': chat.get('username', '')
                    }
    
    if not chats:
        print("Не найдено чатов. Убедитесь, что:", file=sys.stderr)
        print("- Бот добавлен в группу", file=sys.stderr)
        print("- В группе написано сообщение", file=sys.stderr)
        print("- Бот имеет права на отправку сообщений", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("НАЙДЕННЫЕ ЧАТЫ:")
    print("=" * 60)
    
    for chat_id, chat_info in chats.items():
        chat_type_ru = {
            'private': 'Личный чат',
            'group': 'Группа',
            'supergroup': 'Супергруппа',
            'channel': 'Канал'
        }.get(chat_info['type'], chat_info['type'])
        
        print(f"\nТип: {chat_type_ru}")
        print(f"Название: {chat_info['title']}")
        print(f"Chat ID: {chat_id}")
        if chat_info['username']:
            print(f"Username: @{chat_info['username']}")
        print("-" * 60)
    
    print("\nЧтобы использовать группу, скопируйте Chat ID и вставьте в telegram_config.json")
    print("Пример для группы:", file=sys.stderr)
    print(f'  "chat_id": "{list(chats.keys())[0]}"', file=sys.stderr)

if __name__ == "__main__":
    main()

