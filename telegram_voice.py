#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отправки голосовых сообщений в Telegram
Генерирует аудио через MiniMax TTS и отправляет в Telegram
"""

import subprocess
import sys
import os
import json
import io
import requests
import time
import glob
from pathlib import Path

# Устанавливаем UTF-8 для вывода в Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_telegram_config():
    """Получает конфигурацию Telegram из файла"""
    config_file = "telegram_config.json"
    
    if not os.path.exists(config_file):
        # Создаем файл с примером конфигурации
        example_config = {
            "bot_token": "YOUR_BOT_TOKEN_HERE",
            "chat_id": "YOUR_CHAT_ID_HERE",
            "description": {
                "bot_token": "Токен бота от @BotFather в Telegram",
                "chat_id": "ID чата или канала, куда отправлять сообщения. Можно узнать у @userinfobot"
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, ensure_ascii=False, indent=2)
        print(f"Создан файл конфигурации: {config_file}", file=sys.stderr)
        print("Заполните bot_token и chat_id в этом файле", file=sys.stderr)
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
        return None

def convert_mp3_to_ogg(mp3_path):
    """Конвертирует MP3 в OGG для Telegram (если нужно)"""
    ogg_path = mp3_path.replace('.mp3', '.ogg')
    
    # Проверяем, есть ли ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Если ffmpeg нет, пробуем отправить MP3 напрямую (Telegram может принять)
        print("FFmpeg не найден, отправляю MP3 напрямую", file=sys.stderr)
        return mp3_path
    
    # Конвертируем MP3 в OGG
    try:
        subprocess.run([
            'ffmpeg', '-i', mp3_path, 
            '-acodec', 'libopus', 
            '-b:a', '64k',
            ogg_path,
            '-y'  # Перезаписать если существует
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        return ogg_path
    except Exception as e:
        print(f"Ошибка при конвертации: {e}, отправляю MP3", file=sys.stderr)
        return mp3_path

def send_voice_to_telegram(audio_path, bot_token, chat_id, caption=None):
    """Отправляет голосовое сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendVoice"
    
    # Конвертируем в OGG если нужно
    audio_path = convert_mp3_to_ogg(audio_path)
    
    with open(audio_path, 'rb') as audio_file:
        files = {'voice': audio_file}
        data = {'chat_id': chat_id}
        if caption:
            data['caption'] = caption
        
        try:
            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                print(f"Голосовое сообщение отправлено в Telegram", file=sys.stderr)
                return True
            else:
                print(f"Ошибка Telegram API: {result.get('description')}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}", file=sys.stderr)
            return False

def generate_audio(text):
    """Генерирует аудио через text_to_speech.py"""
    print(f"Генерирую аудио из текста ({len(text)} символов)...", file=sys.stderr)
    
    before_time = time.time()
    
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
            return None
        
        # Ищем путь к файлу в stdout
        audio_file = None
        for line in stdout.split('\n'):
            if line.startswith('AUDIO_FILE:'):
                audio_file = line.split('AUDIO_FILE:', 1)[1].strip()
                break
        
        if not audio_file:
            # Ищем последний созданный файл
            time.sleep(0.5)
            audio_dir = "audio"
            if os.path.exists(audio_dir):
                mp3_files = glob.glob(f"{audio_dir}/*.mp3")
                if mp3_files:
                    latest_file = max(mp3_files, key=os.path.getmtime)
                    file_time = os.path.getmtime(latest_file)
                    if file_time >= before_time:
                        audio_file = latest_file
        
        return audio_file if audio_file and os.path.exists(audio_file) else None
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return None

def main():
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
    
    # Получаем текст из аргументов или из speak.py
    if len(sys.argv) < 2:
        print("Использование: python telegram_voice.py <текст>")
        print("Или используйте speak.py для вставки текста в файл", file=sys.stderr)
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    
    # Генерируем аудио
    audio_file = generate_audio(text)
    if not audio_file:
        print("Не удалось создать аудио", file=sys.stderr)
        sys.exit(1)
    
    print(f"Аудио создано: {audio_file}", file=sys.stderr)
    
    # Отправляем в Telegram
    success = send_voice_to_telegram(audio_file, bot_token, chat_id, caption=None)
    
    if success:
        print("Готово! Голосовое сообщение отправлено в Telegram", file=sys.stderr)
    else:
        print("Ошибка при отправке в Telegram", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

