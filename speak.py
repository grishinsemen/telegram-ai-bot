#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для озвучивания текста
Просто вставьте текст между маркерами TEXT_START и TEXT_END ниже, 
затем запустите файл: python speak.py
"""

import subprocess
import sys
import os
import glob
import time
import io

# Устанавливаем UTF-8 для вывода в Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ========== ВСТАВЬТЕ ВАШ ТЕКСТ МЕЖДУ МАРКЕРАМИ ==========
TEXT_START = """
как сейчас под бахмутом?
"""
TEXT_END = """
# ============================================================
"""

def find_latest_audio_file():
    """Находит последний созданный аудиофайл в папке audio/"""
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        return None
    
    mp3_files = glob.glob(f"{audio_dir}/*.mp3")
    if not mp3_files:
        return None
    
    latest_file = max(mp3_files, key=os.path.getmtime)
    return latest_file

def open_audio_file(filepath):
    """Открывает аудиофайл в системе"""
    if not os.path.isabs(filepath):
        filepath = os.path.abspath(filepath)
    
    if sys.platform == 'win32':
        os.startfile(filepath)
    elif sys.platform == 'darwin':
        subprocess.run(['open', filepath])
    else:
        subprocess.run(['xdg-open', filepath])

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
        print("Вставьте текст между TEXT_START и TEXT_END", file=sys.stderr)
        sys.exit(1)
    
    print(f"Текст для озвучивания ({len(text)} символов):", file=sys.stderr)
    print(f"{text[:100]}..." if len(text) > 100 else text, file=sys.stderr)
    print("Генерирую аудио...", file=sys.stderr)
    
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
            print("Открываю файл...", file=sys.stderr)
            open_audio_file(audio_file)
            
            # Проверяем, нужно ли отправить в Telegram
            # Если есть аргумент --telegram или -t, отправляем
            if len(sys.argv) > 1 and ('--telegram' in sys.argv or '-t' in sys.argv):
                try:
                    from telegram_voice import send_voice_to_telegram, get_telegram_config
                    config = get_telegram_config()
                    if config:
                        bot_token = config.get('bot_token')
                        chat_id = config.get('chat_id')
                        if bot_token and bot_token != "YOUR_BOT_TOKEN_HERE" and chat_id and chat_id != "YOUR_CHAT_ID_HERE":
                            print("Отправляю в Telegram...", file=sys.stderr)
                            send_voice_to_telegram(audio_file, bot_token, chat_id, caption=None)
                        else:
                            print("Telegram не настроен. Заполните telegram_config.json", file=sys.stderr)
                except Exception as e:
                    print(f"Ошибка при отправке в Telegram: {e}", file=sys.stderr)
        else:
            print("Не удалось найти созданный аудиофайл", file=sys.stderr)
            
    except subprocess.TimeoutExpired:
        print("Ошибка: таймаут при генерации аудио", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

