# -*- coding: utf-8 -*-
"""Тест OpenRouter API"""
import sys
import json
import requests

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_openrouter(api_key, model="google/gemini-2.0-flash-exp:free"):
    """Тестирует OpenRouter API"""
    print("=" * 60)
    print("Тест подключения к OpenRouter API")
    print("=" * 60)
    
    if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
        print("❌ OpenRouter API ключ не найден в telegram_config.json", file=sys.stderr)
        return False
    
    print(f"🔑 Найден API ключ: {api_key[:20]}...", file=sys.stderr)
    print(f"🧪 Тестирую модель: {model}", file=sys.stderr)
    print("Тестирую подключение к OpenRouter API...", file=sys.stderr)
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Ответь кратко на русском: Привет! Как дела?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/telegram-bot",
        "X-Title": "Telegram Bot"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                content = message.get('content', '')
                if content:
                    print(f"✅ Модель {model} работает!", file=sys.stderr)
                    print(f"📝 Ответ: {content}", file=sys.stderr)
                    return True
            else:
                print(f"⚠️ Модель {model} ответила, но без текста", file=sys.stderr)
                print(f"Ответ API: {json.dumps(result, indent=2, ensure_ascii=False)}", file=sys.stderr)
        else:
            print(f"❌ Ошибка HTTP {response.status_code}", file=sys.stderr)
            try:
                error_data = response.json()
                print(f"Детали ошибки: {json.dumps(error_data, indent=2, ensure_ascii=False)}", file=sys.stderr)
            except:
                print(f"Текст ошибки: {response.text}", file=sys.stderr)
            
            if response.status_code == 401 or response.status_code == 403:
                print("\n❌ Проблема с API ключом. Проверьте:", file=sys.stderr)
                print("1. Правильно ли скопирован ключ из OpenRouter", file=sys.stderr)
                print("2. Не истек ли срок действия ключа", file=sys.stderr)
                print("3. Есть ли у ключа доступ к выбранной модели", file=sys.stderr)
                return False
                
    except requests.exceptions.Timeout:
        print(f"⏱️ Таймаут при обращении к OpenRouter API", file=sys.stderr)
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}", file=sys.stderr)
    
    print("\n❌ Не удалось подключиться к OpenRouter API", file=sys.stderr)
    return False

if __name__ == "__main__":
    # Загружаем конфигурацию
    try:
        with open('telegram_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('openrouter_api_key')
            model = config.get('openrouter_model', 'google/gemini-2.0-flash-exp:free')
            
            if test_openrouter(api_key, model):
                print("\n✅ Успешное подключение к OpenRouter API", file=sys.stderr)
                sys.exit(0)
            else:
                print("\n❌ Ошибка подключения к OpenRouter API", file=sys.stderr)
                print("Проверьте настройки и попробуйте снова.", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)






















