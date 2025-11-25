# -*- coding: utf-8 -*-
"""Проверка Gemini API ключа"""
import sys
import requests
import json

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_key(api_key):
    """Проверяет валидность Gemini API ключа"""
    print("=" * 60)
    print("Проверка Gemini API ключа")
    print("=" * 60)
    print(f"\nКлюч: {api_key[:20]}...{api_key[-5:]}")
    print(f"Длина: {len(api_key)} символов")
    print(f"Начинается с: {api_key[:10]}")
    
    # Пробуем разные способы передачи ключа
    models_to_try = [
        ("gemini-1.5-flash", "v1beta"),
    ]
    
    for model_name, api_version in models_to_try:
        print(f"\n{'='*60}")
        print(f"Тестирую модель: {model_name} (API {api_version})")
        print(f"{'='*60}")
        
        # Способ 1: ключ в URL
        print("\n1. Ключ в URL (query parameter):")
        url1 = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": "Hello"}]}]
        }
        try:
            r1 = requests.post(url1, json=payload, timeout=10)
            print(f"   Status: {r1.status_code}")
            if r1.status_code == 200:
                print("   ✅ УСПЕХ! Ключ работает через URL")
                return True
            else:
                error = r1.json().get('error', {})
                print(f"   ❌ Ошибка: {error.get('message', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Способ 2: ключ в заголовке x-goog-api-key
        print("\n2. Ключ в заголовке x-goog-api-key:")
        url2 = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent"
        headers2 = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        try:
            r2 = requests.post(url2, json=payload, headers=headers2, timeout=10)
            print(f"   Status: {r2.status_code}")
            if r2.status_code == 200:
                print("   ✅ УСПЕХ! Ключ работает через заголовок")
                return True
            else:
                error = r2.json().get('error', {})
                print(f"   ❌ Ошибка: {error.get('message', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Способ 3: ключ в заголовке Authorization
        print("\n3. Ключ в заголовке Authorization (Bearer):")
        headers3 = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        try:
            r3 = requests.post(url2, json=payload, headers=headers3, timeout=10)
            print(f"   Status: {r3.status_code}")
            if r3.status_code == 200:
                print("   ✅ УСПЕХ! Ключ работает через Authorization")
                return True
            else:
                error = r3.json().get('error', {})
                print(f"   ❌ Ошибка: {error.get('message', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
    
    print(f"\n{'='*60}")
    print("❌ Ключ не работает ни одним способом")
    print(f"{'='*60}")
    print("\nВозможные причины:")
    print("1. Ключ неверный или был отозван")
    print("2. Gemini API не включен в Google Cloud Console")
    print("3. Ключ не имеет доступа к Gemini API")
    print("4. Превышен лимит запросов")
    print("\nЧто делать:")
    print("1. Проверьте ключ на https://aistudio.google.com/app/apikey")
    print("2. Убедитесь, что Gemini API включен в вашем проекте")
    print("3. Создайте новый ключ, если старый не работает")
    
    return False

if __name__ == "__main__":
    # Загружаем ключ из конфига
    try:
        with open('telegram_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('gemini_api_key')
            
            if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
                print("❌ Gemini API ключ не найден в telegram_config.json")
                sys.exit(1)
            
            check_key(api_key)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)






















