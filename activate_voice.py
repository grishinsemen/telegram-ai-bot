#!/usr/bin/env python3
"""
Скрипт для активации Voice Design голоса через T2A API
Голос активируется при первом использовании в T2A API
"""

import requests
import json
import sys
import os
from datetime import datetime

def get_api_key():
    """Получает API ключ из конфигурации или переменной окружения"""
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

def get_voices(api_key):
    """Получает список всех доступных голосов"""
    url = "https://api.minimax.io/v1/get_voice"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json={}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении списка голосов: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}", file=sys.stderr)
        return None

def find_voice(voices_data, target_voice_id):
    """Ищет голос в списке доступных голосов"""
    if not voices_data or 'voices' not in voices_data:
        return None
    
    for voice in voices_data['voices']:
        if voice.get('voice_id') == target_voice_id:
            return voice
    
    return None

def activate_voice(api_key, voice_id):
    """
    Активирует голос, используя его в T2A API
    Голос активируется при первом успешном использовании
    """
    url = "https://api.minimax.io/v1/t2a_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Используем короткий текст для активации
    payload = {
        "model": "speech-2.6-hd",
        "text": "Активация голоса",
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
        print(f"Попытка активации голоса: {voice_id}...", file=sys.stderr)
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        result = response.json()
        
        # Проверяем статус ответа
        if 'base_resp' in result:
            status_code = result['base_resp'].get('status_code', 0)
            status_msg = result['base_resp'].get('status_msg', '')
            
            if status_code == 0:
                print("✅ ГОЛОС УСПЕШНО АКТИВИРОВАН!", file=sys.stderr)
                print(f"Голос {voice_id} теперь постоянный и готов к использованию.", file=sys.stderr)
                
                # Сохраняем аудио если есть
                if 'data' in result and 'audio' in result['data']:
                    audio_hex = result['data']['audio']
                    audio_data = bytes.fromhex(audio_hex)
                    
                    audio_dir = "audio"
                    if not os.path.exists(audio_dir):
                        os.makedirs(audio_dir)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_filename = f"{audio_dir}/activation_{timestamp}.mp3"
                    
                    with open(audio_filename, "wb") as f:
                        f.write(audio_data)
                    print(f"Тестовое аудио сохранено: {audio_filename}", file=sys.stderr)
                
                return True
            else:
                print(f"❌ Ошибка активации: {status_msg} (код: {status_code})", file=sys.stderr)
                return False
        else:
            print("⚠️ Неожиданный формат ответа от API", file=sys.stderr)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}", file=sys.stderr)
        return False

def main():
    # Получаем voice_id из аргументов или конфигурации
    if len(sys.argv) > 1:
        voice_id = sys.argv[1]
    else:
        # Пробуем прочитать из конфигурации
        config_file = "tts_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    voice_id = config.get('voice_setting', {}).get('voice_id')
                    if not voice_id:
                        print("Ошибка: Voice ID не найден в конфигурации.", file=sys.stderr)
                        print("Использование: python activate_voice.py <voice_id>", file=sys.stderr)
                        sys.exit(1)
            except Exception as e:
                print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Ошибка: Voice ID не указан.", file=sys.stderr)
            print("Использование: python activate_voice.py <voice_id>", file=sys.stderr)
            sys.exit(1)
    
    print("=" * 80, file=sys.stderr)
    print("АКТИВАЦИЯ VOICE DESIGN ГОЛОСА", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Voice ID: {voice_id}", file=sys.stderr)
    print(file=sys.stderr)
    
    try:
        api_key = get_api_key()
        
        # Сначала проверяем, доступен ли голос
        print("Проверка доступности голоса...", file=sys.stderr)
        voices_data = get_voices(api_key)
        
        if voices_data:
            voice_info = find_voice(voices_data, voice_id)
            if voice_info:
                print(f"✅ Голос найден в вашем аккаунте", file=sys.stderr)
                print(f"   Тип: {voice_info.get('type', 'неизвестно')}", file=sys.stderr)
                print(f"   Название: {voice_info.get('voice_name', 'без названия')}", file=sys.stderr)
            else:
                print(f"⚠️ Голос не найден в списке доступных голосов", file=sys.stderr)
                print(f"   Возможно, голос истек (прошло более 7 дней без использования)", file=sys.stderr)
                print(f"   Или голос еще не создан", file=sys.stderr)
                print(f"   Продолжаем попытку активации...", file=sys.stderr)
        
        print(file=sys.stderr)
        
        # Пытаемся активировать голос
        success = activate_voice(api_key, voice_id)
        
        if success:
            print(file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            print("ГОЛОС АКТИВИРОВАН!", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            print(f"Теперь вы можете использовать голос {voice_id} в text_to_speech.py", file=sys.stderr)
            sys.exit(0)
        else:
            print(file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            print("НЕ УДАЛОСЬ АКТИВИРОВАТЬ ГОЛОС", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            print("Возможные причины:", file=sys.stderr)
            print("1. Голос истек (прошло более 7 дней без использования)", file=sys.stderr)
            print("2. Голос не существует или был удален", file=sys.stderr)
            print("3. Проблема с правами доступа", file=sys.stderr)
            print(file=sys.stderr)
            print("Решение:", file=sys.stderr)
            print("1. Проверьте Voice ID на platform.minimax.io", file=sys.stderr)
            print("2. Создайте новый голос через Voice Design, если старый истек", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()














