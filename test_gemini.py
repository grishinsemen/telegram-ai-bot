# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы Gemini API
"""
import json
import sys
import requests

def test_gemini():
    # Читаем конфигурацию
    try:
        with open('telegram_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
        return False
    
    gemini_api_key = config.get('gemini_api_key')
    
    if not gemini_api_key or gemini_api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("❌ Gemini API ключ не найден в telegram_config.json", file=sys.stderr)
        return False
    
    print(f"🔑 Найден API ключ: {gemini_api_key[:20]}...", file=sys.stderr)
    print("Тестирую подключение к Gemini API...", file=sys.stderr)
    
    # Пробуем разные модели Gemini с правильными endpoints
    models_to_try = [
        ("gemini-2.0-flash-exp", "v1beta"),
        ("gemini-1.5-flash", "v1beta"),
        ("gemini-1.5-pro", "v1beta"),
        ("gemini-pro", "v1beta"),
    ]
    
    test_text = "Привет! Как дела?"
    
    for model_name, api_version in models_to_try:
        print(f"\n🧪 Тестирую модель: {model_name} (API {api_version})", file=sys.stderr)
        
        url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ответь кратко на русском: {test_text}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    if parts and 'text' in parts[0]:
                        answer = parts[0]['text'].strip()
                        print(f"✅ Модель {model_name} работает!", file=sys.stderr)
                        print(f"📝 Ответ: {answer}", file=sys.stderr)
                        return True
                else:
                    print(f"⚠️ Модель {model_name} ответила, но без текста", file=sys.stderr)
                    print(f"Ответ API: {json.dumps(result, indent=2, ensure_ascii=False)}", file=sys.stderr)
            elif response.status_code == 429:
                print(f"⏱️ Превышен лимит для {model_name}, пробую следующую модель...", file=sys.stderr)
                continue
            elif response.status_code == 404:
                print(f"⚠️ Модель {model_name} не найдена, пробую следующую...", file=sys.stderr)
                continue
            else:
                print(f"❌ Ошибка HTTP {response.status_code}", file=sys.stderr)
                try:
                    error_data = response.json()
                    print(f"Детали ошибки: {json.dumps(error_data, indent=2, ensure_ascii=False)}", file=sys.stderr)
                except:
                    print(f"Текст ошибки: {response.text}", file=sys.stderr)
                
                # Если это ошибка авторизации, не пробуем другие модели
                if response.status_code == 401 or response.status_code == 403:
                    print("\n❌ Проблема с API ключом. Проверьте:", file=sys.stderr)
                    print("1. Правильно ли скопирован ключ из Google AI Studio", file=sys.stderr)
                    print("2. Не истек ли срок действия ключа", file=sys.stderr)
                    print("3. Включен ли Gemini API в вашем проекте Google Cloud", file=sys.stderr)
                    return False
                    
        except requests.exceptions.Timeout:
            print(f"⏱️ Таймаут при обращении к модели {model_name}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"❌ Ошибка при тестировании {model_name}: {e}", file=sys.stderr)
            continue
    
    print("\n❌ Не удалось подключиться ни к одной модели Gemini", file=sys.stderr)
    return False

if __name__ == "__main__":
    print("=" * 50, file=sys.stderr)
    print("Тест подключения к Gemini API", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print()
    
    if test_gemini():
        print("\n✅ Gemini API работает корректно!", file=sys.stderr)
        print("Бот готов к использованию.", file=sys.stderr)
        sys.exit(0)
    else:
        print("\n❌ Проблемы с подключением к Gemini API", file=sys.stderr)
        print("Проверьте настройки и попробуйте снова.", file=sys.stderr)
        sys.exit(1)

