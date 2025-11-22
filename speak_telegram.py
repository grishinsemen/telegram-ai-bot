#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для озвучивания текста и отправки в Telegram
Просто вставьте текст между маркерами TEXT_START и TEXT_END ниже, 
затем запустите файл: python speak_telegram.py
"""

import subprocess
import sys
import os
import glob
import time
import io
import json
import requests

# Устанавливаем UTF-8 для вывода в Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ========== ВСТАВЬТЕ ВАШ ТЕКСТ МЕЖДУ МАРКЕРАМИ ==========
TEXT_START = """
хороших выходных вам, господа

"""
TEXT_END = """
# ============================================================
"""

def get_telegram_config():
    """Получает конфигурацию Telegram"""
    config_file = "telegram_config.json"
    if not os.path.exists(config_file):
        print(f"Файл {config_file} не найден. Создайте его с bot_token и chat_id", file=sys.stderr)
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
        return None

def find_latest_audio_file():
    """Находит последний созданный аудиофайл"""
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        return None
    
    mp3_files = glob.glob(f"{audio_dir}/*.mp3")
    if not mp3_files:
        return None
    
    latest_file = max(mp3_files, key=os.path.getmtime)
    return latest_file

def send_voice_to_telegram(audio_path, bot_token, chat_id, caption=None):
    """Отправляет голосовое сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendVoice"
    
    # Telegram принимает MP3, но лучше OGG. Пробуем MP3 напрямую
    with open(audio_path, 'rb') as audio_file:
        files = {'voice': audio_file}
        data = {'chat_id': chat_id}
        if caption:
            data['caption'] = caption[:200]  # Ограничение Telegram
        
        try:
            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                return True
            else:
                print(f"Ошибка Telegram API: {result.get('description')}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}", file=sys.stderr)
            return False

def main():
    # Извлекаем текст между маркерами
    script_path = __file__
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим текст между маркерами
    start_marker = 'TEXT_START = """'
    end_marker = '"""'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Ошибка: не найден маркер TEXT_START", file=sys.stderr)
        sys.exit(1)
    
    start_idx += len(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        print("Ошибка: не найден закрывающий маркер", file=sys.stderr)
        sys.exit(1)
    
    text = content[start_idx:end_idx].strip()
    
    if not text:
        print("Ошибка: текст не найден между маркерами", file=sys.stderr)
        sys.exit(1)
    
    print(f"Текст для озвучивания ({len(text)} символов)", file=sys.stderr)
    print("Генерирую аудио...", file=sys.stderr)
    
    # Получаем конфигурацию Telegram
    config = get_telegram_config()
    if not config:
        sys.exit(1)
    
    bot_token = config.get('bot_token')
    chat_id = config.get('chat_id')
    
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("Ошибка: bot_token не настроен в telegram_config.json", file=sys.stderr)
        sys.exit(1)
    
    if not chat_id or chat_id == "YOUR_CHAT_ID_HERE":
        print("Ошибка: chat_id не настроен в telegram_config.json", file=sys.stderr)
        sys.exit(1)
    
    # Запоминаем время перед созданием файла
    before_time = time.time()
    
    # Запускаем text_to_speech.py
    try:
        process = subprocess.Popen(
            [sys.executable, "text_to_speech.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        stdout, stderr = process.communicate(input=text, timeout=120)
        
        if process.returncode != 0:
            print(f"Ошибка при генерации аудио:\n{stderr}", file=sys.stderr)
            sys.exit(1)
        
        # Ищем путь к файлу в stdout
        audio_file = None
        for line in stdout.split('\n'):
            if line.startswith('AUDIO_FILE:'):
                audio_file = line.split('AUDIO_FILE:', 1)[1].strip()
                break
        
        # Если не нашли в stdout, ищем последний созданный файл
        if not audio_file:
            time.sleep(0.5)
            latest_file = find_latest_audio_file()
            if latest_file:
                file_time = os.path.getmtime(latest_file)
                if file_time >= before_time:
                    audio_file = latest_file
        
        if audio_file and os.path.exists(audio_file):
            print(f"Аудиофайл создан: {audio_file}", file=sys.stderr)
            print("Отправляю в Telegram...", file=sys.stderr)
            
            success = send_voice_to_telegram(audio_file, bot_token, chat_id, caption=None)
            
            if success:
                print("Готово! Голосовое сообщение отправлено в Telegram", file=sys.stderr)
            else:
                print("Ошибка при отправке в Telegram", file=sys.stderr)
                sys.exit(1)
        else:
            print("Не удалось найти созданный аудиофайл", file=sys.stderr)
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("Ошибка: таймаут при генерации аудио", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

