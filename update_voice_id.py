#!/usr/bin/env python3
"""
Скрипт для быстрого обновления voice_id в конфигурации
"""

import json
import sys
import os

CONFIG_FILE = "tts_config.json"

def update_voice_id(voice_id):
    """Обновляет voice_id в конфигурации"""
    if not os.path.exists(CONFIG_FILE):
        print(f"Файл {CONFIG_FILE} не найден!", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        old_voice_id = config['voice_setting']['voice_id']
        config['voice_setting']['voice_id'] = voice_id
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"Voice ID обновлен:")
        print(f"  Было: {old_voice_id}")
        print(f"  Стало: {voice_id}")
        print()
        print(f"Конфигурация сохранена в {CONFIG_FILE}")
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Использование: python update_voice_id.py <voice_id>")
        print()
        print("Пример:")
        print("  python update_voice_id.py your-cloned-voice-id")
        print()
        print("Сначала получите список доступных голосов:")
        print("  python list_voices.py")
        sys.exit(1)
    
    voice_id = sys.argv[1]
    update_voice_id(voice_id)

if __name__ == "__main__":
    main()

