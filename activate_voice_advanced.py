#!/usr/bin/env python3
"""
Расширенный скрипт для активации Voice Design голоса
Пробует разные варианты параметров и моделей
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

def try_activate(api_key, voice_id, model, text="Тест"):
    """Пробует активировать голос с заданными параметрами"""
    url = "https://api.minimax.io/v1/t2a_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
            "english_normalization": False
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
            "force_cbr": False
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if 'base_resp' in result:
            status_code = result['base_resp'].get('status_code', 0)
            status_msg = result['base_resp'].get('status_msg', '')
            
            if status_code == 0:
                return True, "Успешно"
            else:
                return False, f"{status_msg} (код: {status_code})"
        else:
            return False, "Неожиданный формат ответа"
            
    except Exception as e:
        return False, str(e)

def main():
    if len(sys.argv) < 2:
        print("Использование: python activate_voice_advanced.py <voice_id>", file=sys.stderr)
        sys.exit(1)
    
    voice_id = sys.argv[1]
    
    print("=" * 80, file=sys.stderr)
    print("РАСШИРЕННАЯ АКТИВАЦИЯ VOICE DESIGN ГОЛОСА", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Voice ID: {voice_id}", file=sys.stderr)
    print(file=sys.stderr)
    
    api_key = get_api_key()
    
    # Пробуем разные модели
    models = [
        "speech-2.6-hd",
        "speech-2.6-turbo",
        "speech-02-hd",
        "speech-02-turbo"
    ]
    
    texts = [
        "Тест",
        "Активация",
        "Hello",
        "Привет"
    ]
    
    success = False
    
    for model in models:
        print(f"Пробую модель: {model}...", file=sys.stderr)
        for text in texts:
            result, msg = try_activate(api_key, voice_id, model, text)
            if result:
                print(f"✅ УСПЕХ! Модель: {model}, Текст: {text}", file=sys.stderr)
                print(f"Голос {voice_id} активирован!", file=sys.stderr)
                success = True
                break
            else:
                print(f"   Текст '{text}': {msg}", file=sys.stderr)
        
        if success:
            break
        print(file=sys.stderr)
    
    if not success:
        print("=" * 80, file=sys.stderr)
        print("НЕ УДАЛОСЬ АКТИВИРОВАТЬ ГОЛОС", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        print("Возможные причины:", file=sys.stderr)
        print("1. Голос истек (прошло более 7 дней без использования)", file=sys.stderr)
        print("2. Голос был удален", file=sys.stderr)
        print("3. Голос не существует в вашем аккаунте", file=sys.stderr)
        print("4. Проблема с правами доступа", file=sys.stderr)
        print(file=sys.stderr)
        print("РЕШЕНИЕ:", file=sys.stderr)
        print("1. Зайдите на https://platform.minimax.io/", file=sys.stderr)
        print("2. Перейдите в раздел Voice Design", file=sys.stderr)
        print("3. Проверьте, существует ли голос с таким ID", file=sys.stderr)
        print("4. Если голос истек, создайте новый", file=sys.stderr)
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()














