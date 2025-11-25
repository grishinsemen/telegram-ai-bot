#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Быстрый тест бота"""

import sys
import json
import requests
from telegram_bot import BotConfig, get_config, get_bot_info, should_respond

def test_bot():
    print("=" * 60)
    print("🧪 ТЕСТ БОТА")
    print("=" * 60)
    
    # Загружаем конфигурацию
    config = get_config()
    if not config:
        print("❌ Не удалось загрузить конфигурацию")
        return False
    
    print(f"\n✅ Конфигурация загружена")
    print(f"   Bot token: {config.bot_token[:20]}...")
    print(f"   Chat ID: {config.chat_id}")
    
    # Проверяем бота
    session = requests.Session()
    bot_info = get_bot_info(config.bot_token, session)
    if not bot_info:
        print("❌ Не удалось получить информацию о боте")
        return False
    
    bot_username = bot_info.get('username')
    print(f"✅ Бот найден: @{bot_username}")
    
    # Проверяем получение обновлений
    print("\n📬 Проверяю получение обновлений...")
    url = f"https://api.telegram.org/bot{config.bot_token}/getUpdates"
    try:
        response = session.get(url, params={'offset': -1, 'limit': 1}, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('ok'):
            updates = result.get('result', [])
            print(f"✅ Telegram API работает. Последних обновлений: {len(updates)}")
            if updates:
                print(f"   Последний update_id: {updates[-1].get('update_id')}")
        else:
            print(f"❌ Ошибка Telegram API: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при получении обновлений: {e}")
        return False
    
    # Тестируем should_respond
    print("\n🧪 Тестирую should_respond...")
    
    # Тест 1: Сообщение с вопросом
    test_message1 = {'text': 'Привет, как дела?'}
    result1 = should_respond(test_message1, bot_username)
    print(f"   Тест 1 (вопрос): {result1} {'✅' if result1 else '❌'}")
    
    # Тест 2: Сообщение с ключевым словом
    test_message2 = {'text': 'Бот, помоги мне'}
    result2 = should_respond(test_message2, bot_username)
    print(f"   Тест 2 (ключевое слово): {result2} {'✅' if result2 else '❌'}")
    
    # Тест 3: Обычное сообщение
    test_message3 = {'text': 'Привет всем'}
    result3 = should_respond(test_message3, bot_username)
    print(f"   Тест 3 (обычное сообщение): {result3} {'✅' if not result3 else '❌'}")
    
    # Тест 4: Упоминание бота
    test_message4 = {'text': f'Привет @{bot_username}, как дела?'}
    result4 = should_respond(test_message4, bot_username)
    print(f"   Тест 4 (упоминание): {result4} {'✅' if result4 else '❌'}")
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_bot()

