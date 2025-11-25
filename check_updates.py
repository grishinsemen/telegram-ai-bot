#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка обновлений бота"""

import sys
import json
import requests
from telegram_bot import get_config, LAST_UPDATE_ID_FILE
import os

def check_updates():
    config = get_config()
    if not config:
        print("❌ Не удалось загрузить конфигурацию")
        return
    
    session = requests.Session()
    
    # Читаем текущий last_update_id
    current_offset = 0
    if os.path.exists(LAST_UPDATE_ID_FILE):
        try:
            with open(LAST_UPDATE_ID_FILE, 'r') as f:
                current_offset = int(f.read().strip())
        except:
            pass
    
    print(f"📋 Текущий offset: {current_offset}")
    print(f"📋 Будем запрашивать с offset: {current_offset + 1}")
    
    # Получаем обновления
    url = f"https://api.telegram.org/bot{config.bot_token}/getUpdates"
    params = {
        'offset': current_offset + 1,
        'timeout': 5,
        'limit': 10
    }
    
    print("\n📬 Запрашиваю обновления...")
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if not result.get('ok'):
            print(f"❌ Ошибка: {result.get('description')}")
            return
        
        updates = result.get('result', [])
        print(f"✅ Получено обновлений: {len(updates)}")
        
        if not updates:
            print("\n⚠️ Нет новых обновлений")
            print("   Попробуйте отправить сообщение в чат и запустить бота снова")
            return
        
        print("\n📋 Список обновлений:")
        for i, update in enumerate(updates, 1):
            update_id = update.get('update_id')
            message = update.get('message')
            
            if message:
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '') or message.get('caption', '')
                from_user = message.get('from', {})
                username = from_user.get('username', 'без username')
                
                print(f"\n   Обновление #{i} (update_id={update_id}):")
                print(f"      Chat ID: {chat_id} (ожидаемый: {config.chat_id})")
                print(f"      От: @{username}")
                print(f"      Текст: {text[:50] if text else '(нет текста)'}")
                
                if str(chat_id) != str(config.chat_id):
                    print(f"      ⚠️ Неправильный chat_id - бот пропустит это сообщение")
                else:
                    print(f"      ✅ Правильный chat_id")
            else:
                print(f"\n   Обновление #{i} (update_id={update_id}): без сообщения")
        
        print(f"\n💡 Совет: Если видите обновления с правильным chat_id, но бот не отвечает,")
        print(f"   проверьте логи бота - возможно, сообщения не проходят проверку should_respond")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_updates()

