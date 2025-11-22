#!/usr/bin/env python3
"""
Скрипт для получения списка доступных голосов из аккаунта MiniMax
Включает системные голоса, клонированные голоса, Voice Design и т.д.
"""

import requests
import json
import sys
import os

def get_api_key():
    """Получает API ключ из конфигурации или переменной окружения"""
    api_key = os.getenv('MINIMAX_API_KEY')
    
    if not api_key:
        # Сначала пробуем локальный файл mcp.json в папке проекта
        local_config = "mcp.json"
        config_path = None
        
        if os.path.exists(local_config):
            config_path = local_config
        else:
            # Если локального нет, пробуем системный файл Cursor
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

def get_voices(api_key, voice_type="all"):
    """
    Получает список всех доступных голосов через Get Voice API
    voice_type: "system", "voice_cloning", "voice_generation", "music_generation", "all"
    """
    # Правильный endpoint согласно документации
    url = "https://api.minimax.io/v1/get_voice"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # POST запрос с параметром voice_type согласно MCP документации
    payload = {
        "voice_type": voice_type
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}", file=sys.stderr)
        raise

def display_voices(voices_data):
    """Отображает список голосов в удобном формате"""
    print("=" * 80)
    print("ДОСТУПНЫЕ ГОЛОСА В ВАШЕМ АККАУНТЕ MINIMAX")
    print("=" * 80)
    print()
    
    # API возвращает голоса в разных категориях
    system_voices = voices_data.get('system_voice', []) or []
    voice_cloning = voices_data.get('voice_cloning', []) or []
    voice_generation = voices_data.get('voice_generation', []) or []  # Voice Design
    music_generation = voices_data.get('music_generation', []) or []
    
    # Отображаем Voice Design голоса (voice_generation) - самое важное
    if voice_generation:
        print("[ГОЛОСА VOICE DESIGN]")
        print("-" * 80)
        for i, voice in enumerate(voice_generation, 1):
            voice_id = voice.get('voice_id', '')
            voice_name = voice.get('voice_name', 'Без названия') or 'Без названия'
            created_time = voice.get('created_time', '')
            print(f"{i}. Voice ID: {voice_id}")
            print(f"   Название: {voice_name}")
            if created_time:
                print(f"   Создан: {created_time}")
            print()
    
    # Отображаем клонированные голоса
    if voice_cloning:
        print("[КЛОНИРОВАННЫЕ ГОЛОСА]")
        print("-" * 80)
        for i, voice in enumerate(voice_cloning, 1):
            voice_id = voice.get('voice_id', '')
            voice_name = voice.get('voice_name', 'Без названия') or 'Без названия'
            created_time = voice.get('created_time', '')
            print(f"{i}. Voice ID: {voice_id}")
            print(f"   Название: {voice_name}")
            if created_time:
                print(f"   Создан: {created_time}")
            print()
    
    # Отображаем системные голоса (первые 10)
    if system_voices:
        print("[СИСТЕМНЫЕ ГОЛОСА] (показаны первые 10)")
        print("-" * 80)
        for i, voice in enumerate(system_voices[:10], 1):
            voice_id = voice.get('voice_id', '')
            voice_name = voice.get('voice_name', 'Без названия') or 'Без названия'
            print(f"{i}. Voice ID: {voice_id}")
            print(f"   Название: {voice_name}")
        if len(system_voices) > 10:
            print(f"\n... и еще {len(system_voices) - 10} системных голосов")
        print()
    
    # Статистика
    print("=" * 80)
    print("СТАТИСТИКА:")
    print(f"  Voice Design голоса: {len(voice_generation)}")
    print(f"  Клонированные голоса: {len(voice_cloning)}")
    print(f"  Системные голоса: {len(system_voices)}")
    print(f"  Музыкальные голоса: {len(music_generation)}")
    total = len(voice_generation) + len(voice_cloning) + len(system_voices) + len(music_generation)
    print(f"  ВСЕГО: {total}")
    print("=" * 80)
    print()
    
    # Сохраняем в файл для удобства
    output_file = "available_voices.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(voices_data, f, ensure_ascii=False, indent=2)
    print(f"Полный список сохранен в: {output_file}")
    print()
    
    # Показываем, как использовать
    if voice_cloning:
        print("КАК ИСПОЛЬЗОВАТЬ КЛОНИРОВАННЫЙ ГОЛОС:")
        print("-" * 80)
        clone_voice_id = voice_cloning[0].get('voice_id', '')
        print(f"1. Откройте файл tts_config.json")
        print(f"2. Найдите поле \"voice_id\" в разделе \"voice_setting\"")
        print(f"3. Замените значение на: {clone_voice_id}")
        print(f"4. Сохраните файл")
        print()
        print("Или используйте команду:")
        print(f"python update_voice_id.py {clone_voice_id}")

def main():
    try:
        print("Получение списка голосов из вашего аккаунта MiniMax...")
        print()
        
        api_key = get_api_key()
        voices_data = get_voices(api_key)
        display_voices(voices_data)
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

