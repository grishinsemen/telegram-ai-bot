#!/usr/bin/env python3
"""
Скрипт для тестирования Voice ID и получения информации об ошибке
"""

import requests
import json
import sys
import os

def get_api_key():
    """Получает API ключ"""
    api_key = os.getenv('MINIMAX_API_KEY')
    
    if not api_key:
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
                                break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
            except Exception as e:
                print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Ошибка: API ключ не найден.", file=sys.stderr)
        sys.exit(1)
    
    return api_key

def test_voice_id(voice_id, api_key):
    """Тестирует Voice ID с коротким текстом"""
    url = "https://api.minimax.io/v1/t2a_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "speech-2.6-hd",
        "text": "Тест",
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            print(f"[OK] Voice ID '{voice_id}' работает!")
            return True
        else:
            print(f"[ERROR] Voice ID '{voice_id}' не работает")
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # Анализируем ошибку
            if 'base_resp' in result:
                status_code = result['base_resp'].get('status_code')
                status_msg = result['base_resp'].get('status_msg', '')
                
                print()
                print("АНАЛИЗ ОШИБКИ:")
                if status_code == 1004 or 'voice' in status_msg.lower() or 'access' in status_msg.lower():
                    print("  - Voice ID не найден или недоступен")
                    print("  - Возможные причины:")
                    print("    1. Voice ID указан неправильно")
                    print("    2. Голос истек (не использовался 7 дней)")
                    print("    3. Голос принадлежит другому аккаунту")
                    print("    4. Голос еще не активирован (нужно использовать в T2A)")
                    print()
                    print("  РЕШЕНИЕ:")
                    print("    1. Проверьте Voice ID в веб-интерфейсе MiniMax")
                    print("    2. Убедитесь, что голос активен")
                    print("    3. Попробуйте использовать голос через веб-интерфейс для активации")
            
            return False
            
    except Exception as e:
        print(f"Ошибка при тестировании: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 2:
        print("Использование: python test_voice_id.py <voice_id>")
        print()
        print("Пример:")
        print("  python test_voice_id.py your-voice-id")
        print()
        print("Или протестируйте текущий Voice ID из конфигурации:")
        print("  python test_voice_id.py --current")
        sys.exit(1)
    
    api_key = get_api_key()
    
    if sys.argv[1] == "--current":
        # Читаем из конфигурации
        try:
            with open("tts_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
                voice_id = config['voice_setting']['voice_id']
                print(f"Тестирование текущего Voice ID из конфигурации: {voice_id}")
        except Exception as e:
            print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        voice_id = sys.argv[1]
    
    print(f"Тестирование Voice ID: {voice_id}")
    print("-" * 60)
    print()
    
    test_voice_id(voice_id, api_key)

if __name__ == "__main__":
    main()

