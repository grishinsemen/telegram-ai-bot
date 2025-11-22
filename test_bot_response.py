#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы бота
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

def test_zenmux():
    """Тестирует ZenMux API"""
    config_file = "telegram_config.json"
    if not os.path.exists(config_file):
        print("❌ Файл telegram_config.json не найден", file=sys.stderr)
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка при чтении конфигурации: {e}", file=sys.stderr)
        return False
    
    zenmux_api_key = config.get('zenmux_api_key')
    zenmux_model = config.get('zenmux_model', 'google/gemini-3-pro-preview-free')
    zenmux_base_url = config.get('zenmux_base_url', 'https://zenmux.ai/api/v1')
    
    if not zenmux_api_key or zenmux_api_key == "YOUR_ZENMUX_API_KEY_HERE":
        print("❌ ZenMux API ключ не настроен", file=sys.stderr)
        return False
    
    print(f"🧪 Тестирую ZenMux API...", file=sys.stderr)
    print(f"   Основная модель: {zenmux_model}", file=sys.stderr)
    
    # Получаем запасные модели из конфига
    fallback_models = config.get('fallback_models', ["google/gemini-3-pro-preview"])
    if fallback_models:
        print(f"   Запасные модели ZenMux: {', '.join(fallback_models)}", file=sys.stderr)
    
    # Проверяем OpenRouter
    openrouter_api_key = config.get('openrouter_api_key')
    openrouter_model = config.get('openrouter_model', 'openai/gpt-4o-mini')
    if openrouter_api_key and openrouter_api_key != "YOUR_OPENROUTER_API_KEY_HERE":
        print(f"   OpenRouter (запасной): {openrouter_model}", file=sys.stderr)
    
    print(f"   URL: {zenmux_base_url}", file=sys.stderr)
    
    # Список моделей для тестирования (в порядке приоритета)
    models_to_try = [zenmux_model]
    
    # Добавляем запасные модели из конфига
    if fallback_models:
        for fallback_model in fallback_models:
            if fallback_model not in models_to_try:
                models_to_try.append(fallback_model)
    
    for model in models_to_try:
        print(f"\n   Пробую модель: {model}", file=sys.stderr)
        url = f"{zenmux_base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Привет! Ответь одним предложением."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        headers = {
            "Authorization": f"Bearer {zenmux_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"      Статус: {response.status_code}", file=sys.stderr)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', '')
                    if not content and 'reasoning' in message:
                        content = message.get('reasoning', '')
                    if content:
                        print(f"✅ ZenMux работает с моделью {model}!", file=sys.stderr)
                        print(f"   Ответ: {content[:100]}...", file=sys.stderr)
                        return True
                    else:
                        print(f"      ⚠️ Модель ответила, но content пустой", file=sys.stderr)
                else:
                    print(f"      ⚠️ Модель ответила, но нет choices в ответе", file=sys.stderr)
            elif response.status_code == 429:
                print(f"      ⚠️ Превышен лимит запросов (429) для модели {model}", file=sys.stderr)
            else:
                print(f"      ❌ Ошибка для модели {model}: {response.status_code}", file=sys.stderr)
                print(f"      Ответ: {response.text[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"      ❌ Ошибка при вызове модели {model}: {e}", file=sys.stderr)
    
    # Если ZenMux не сработал, пробуем OpenRouter
    openrouter_api_key = config.get('openrouter_api_key')
    openrouter_model = config.get('openrouter_model', 'openai/gpt-4o-mini')
    
    if openrouter_api_key and openrouter_api_key != "YOUR_OPENROUTER_API_KEY_HERE":
        print(f"\n   Пробую OpenRouter: {openrouter_model}", file=sys.stderr)
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        payload = {
            "model": openrouter_model,
            "messages": [
                {
                    "role": "user",
                    "content": "Привет! Ответь одним предложением."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/telegram-bot",
            "X-Title": "Telegram Bot"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"      Статус: {response.status_code}", file=sys.stderr)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', '')
                    if content:
                        print(f"✅ OpenRouter работает с моделью {openrouter_model}!", file=sys.stderr)
                        print(f"   Ответ: {content[:100]}...", file=sys.stderr)
                        return True
            elif response.status_code == 429:
                print(f"      ⚠️ Превышен лимит запросов (429) для OpenRouter", file=sys.stderr)
            else:
                print(f"      ❌ Ошибка для OpenRouter: {response.status_code}", file=sys.stderr)
                print(f"      Ответ: {response.text[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"      ❌ Ошибка при вызове OpenRouter: {e}", file=sys.stderr)
    
    return False

def test_telegram_bot():
    """Тестирует подключение к Telegram боту"""
    config_file = "telegram_config.json"
    if not os.path.exists(config_file):
        print("❌ Файл telegram_config.json не найден", file=sys.stderr)
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка при чтении конфигурации: {e}", file=sys.stderr)
        return False
    
    bot_token = config.get('bot_token')
    chat_id = config.get('chat_id')
    
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Bot token не настроен", file=sys.stderr)
        return False
    
    print(f"🧪 Тестирую Telegram бота...", file=sys.stderr)
    
    # Проверяем информацию о боте
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                print(f"✅ Бот найден: @{bot_info.get('username')} ({bot_info.get('first_name')})", file=sys.stderr)
                
                # Проверяем, может ли бот получать обновления
                updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
                updates_response = requests.get(updates_url, params={'limit': 1}, timeout=10)
                if updates_response.status_code == 200:
                    updates_result = updates_response.json()
                    if updates_result.get('ok'):
                        print(f"✅ Бот может получать обновления", file=sys.stderr)
                        return True
                    else:
                        print(f"⚠️ Бот не может получать обновления: {updates_result.get('description')}", file=sys.stderr)
                else:
                    print(f"⚠️ Ошибка при получении обновлений: {updates_response.status_code}", file=sys.stderr)
            else:
                print(f"❌ Ошибка: {result.get('description')}", file=sys.stderr)
        else:
            print(f"❌ Ошибка при подключении к Telegram API: {response.status_code}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
    
    return False

if __name__ == "__main__":
    print("\n" + "=" * 60, file=sys.stderr)
    print("🧪 ТЕСТИРОВАНИЕ БОТА", file=sys.stderr)
    print("=" * 60 + "\n", file=sys.stderr)
    
    telegram_ok = test_telegram_bot()
    print("", file=sys.stderr)
    zenmux_ok = test_zenmux()
    
    print("\n" + "=" * 60, file=sys.stderr)
    if telegram_ok and zenmux_ok:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(0)
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(1)
