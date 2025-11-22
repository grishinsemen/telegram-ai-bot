#!/usr/bin/env python3
"""
Скрипт для просмотра и редактирования настроек Text2Speech
"""

import json
import sys
import os

CONFIG_FILE = "tts_config.json"

def load_config():
    """Загружает конфигурацию из файла"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"Файл конфигурации {CONFIG_FILE} не найден!", file=sys.stderr)
        sys.exit(1)

def save_config(config):
    """Сохраняет конфигурацию в файл"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"Конфигурация сохранена в {CONFIG_FILE}")

def show_config(config):
    """Отображает текущие настройки"""
    print("=" * 60)
    print("НАСТРОЙКИ MINIMAX TEXT2SPEECH")
    print("=" * 60)
    print()
    
    print("[МОДЕЛЬ]")
    print(f"   Модель: {config['model']}")
    if 'description' in config and 'model' in config['description']:
        print(f"   {config['description']['model']}")
    print()
    
    print("[НАСТРОЙКИ ГОЛОСА]")
    vs = config['voice_setting']
    print(f"   Voice ID: {vs['voice_id']}")
    if 'description' in config and 'voice_id' in config['description']:
        print(f"   {config['description']['voice_id']}")
    print(f"   Скорость (speed): {vs['speed']}")
    if 'description' in config and 'speed' in config['description']:
        print(f"   {config['description']['speed']}")
    print(f"   Громкость (vol): {vs['vol']}")
    if 'description' in config and 'vol' in config['description']:
        print(f"   {config['description']['vol']}")
    print(f"   Высота тона (pitch): {vs.get('pitch', 0)}")
    if 'description' in config and 'pitch' in config['description']:
        print(f"   {config['description']['pitch']}")
    print(f"   English normalization: {vs.get('english_normalization', False)}")
    print()
    
    print("[НАСТРОЙКИ АУДИО]")
    as_set = config['audio_setting']
    print(f"   Частота дискретизации (sample_rate): {as_set['sample_rate']} Hz")
    if 'description' in config and 'sample_rate' in config['description']:
        print(f"   {config['description']['sample_rate']}")
    print(f"   Битрейт (bitrate): {as_set['bitrate']} bps")
    if 'description' in config and 'bitrate' in config['description']:
        print(f"   {config['description']['bitrate']}")
    print(f"   Формат (format): {as_set['format']}")
    if 'description' in config and 'format' in config['description']:
        print(f"   {config['description']['format']}")
    print(f"   Каналы (channel): {as_set['channel']}")
    if 'description' in config and 'channel' in config['description']:
        print(f"   {config['description']['channel']}")
    if 'force_cbr' in as_set:
        print(f"   Force CBR: {as_set['force_cbr']}")
    print()
    
    print("[ДРУГИЕ НАСТРОЙКИ]")
    print(f"   Stream: {config.get('stream', False)}")
    print()
    
    print("=" * 60)

def edit_config_interactive(config):
    """Интерактивное редактирование настроек"""
    print("\nРедактирование настроек (нажмите Enter для пропуска):")
    print()
    
    # Модель
    new_model = input(f"Модель [{config['model']}]: ").strip()
    if new_model:
        config['model'] = new_model
    
    # Voice ID
    new_voice = input(f"Voice ID [{config['voice_setting']['voice_id']}]: ").strip()
    if new_voice:
        config['voice_setting']['voice_id'] = new_voice
    
    # Speed
    try:
        new_speed = input(f"Скорость (0.5-2.0) [{config['voice_setting']['speed']}]: ").strip()
        if new_speed:
            config['voice_setting']['speed'] = float(new_speed)
    except ValueError:
        print("Неверное значение скорости, используется значение по умолчанию")
    
    # Volume
    try:
        new_vol = input(f"Громкость (0.0-1.0) [{config['voice_setting']['vol']}]: ").strip()
        if new_vol:
            config['voice_setting']['vol'] = float(new_vol)
    except ValueError:
        print("Неверное значение громкости, используется значение по умолчанию")
    
    # Pitch
    try:
        new_pitch = input(f"Высота тона (-12 до +12) [{config['voice_setting'].get('pitch', 0)}]: ").strip()
        if new_pitch:
            config['voice_setting']['pitch'] = int(new_pitch)
    except ValueError:
        print("Неверное значение высоты тона, используется значение по умолчанию")
    
    # Sample rate
    try:
        new_sr = input(f"Частота дискретизации [{config['audio_setting']['sample_rate']}]: ").strip()
        if new_sr:
            config['audio_setting']['sample_rate'] = int(new_sr)
    except ValueError:
        print("Неверное значение частоты дискретизации")
    
    # Bitrate
    try:
        new_br = input(f"Битрейт [{config['audio_setting']['bitrate']}]: ").strip()
        if new_br:
            config['audio_setting']['bitrate'] = int(new_br)
    except ValueError:
        print("Неверное значение битрейта")
    
    # Format
    new_format = input(f"Формат (mp3/pcm/flac/wav) [{config['audio_setting']['format']}]: ").strip()
    if new_format:
        config['audio_setting']['format'] = new_format
    
    # Channel
    try:
        new_ch = input(f"Каналы (1/2) [{config['audio_setting']['channel']}]: ").strip()
        if new_ch:
            config['audio_setting']['channel'] = int(new_ch)
    except ValueError:
        print("Неверное значение каналов")
    
    return config

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--edit":
        config = load_config()
        show_config(config)
        config = edit_config_interactive(config)
        save_config(config)
        print("\nОбновленные настройки:")
        show_config(config)
    else:
        config = load_config()
        show_config(config)
        print("\nДля редактирования запустите: python tts_settings.py --edit")

if __name__ == "__main__":
    main()

