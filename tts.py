#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая обертка для text_to_speech.py
Обрабатывает формат "-текст" и автоматически открывает созданный аудиофайл
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

def find_latest_audio_file():
    """Находит последний созданный аудиофайл в папке audio/"""
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        return None
    
    # Находим все MP3 файлы
    mp3_files = glob.glob(f"{audio_dir}/*.mp3")
    if not mp3_files:
        return None
    
    # Сортируем по времени модификации и берем последний
    latest_file = max(mp3_files, key=os.path.getmtime)
    return latest_file

def open_audio_file(filepath):
    """Открывает аудиофайл в системе"""
    # Преобразуем относительный путь в абсолютный
    if not os.path.isabs(filepath):
        filepath = os.path.abspath(filepath)
    
    if sys.platform == 'win32':
        # Windows
        os.startfile(filepath)
    elif sys.platform == 'darwin':
        # macOS
        subprocess.run(['open', filepath])
    else:
        # Linux
        subprocess.run(['xdg-open', filepath])

def main():
    if len(sys.argv) < 2:
        print("Использование: python tts.py -<текст для озвучивания>")
        print("Пример: python tts.py -Привет, как дела?")
        sys.exit(1)
    
    # Получаем текст (все аргументы после имени скрипта)
    text = " ".join(sys.argv[1:])
    
    # Убираем начальный "-" если есть
    if text.startswith("-"):
        text = text[1:].strip()
    
    # Если текст начинается с "@", это путь к файлу
    if text.startswith("@"):
        filepath = text[1:].strip()
        try:
            # Читаем файл как байты и пробуем разные кодировки
            with open(filepath, 'rb') as f:
                raw_bytes = f.read()
            
            # Пробуем разные кодировки
            text_read = False
            for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
                try:
                    text = raw_bytes.decode(encoding).strip()
                    # Проверяем, что текст содержит кириллицу
                    if any('\u0400' <= c <= '\u04FF' for c in text):
                        text_read = True
                        print(f"Файл прочитан с кодировкой: {encoding}", file=sys.stderr)
                        break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if not text_read:
                # Если ничего не подошло, используем utf-8 с заменой ошибок
                text = raw_bytes.decode('utf-8', errors='replace').strip()
                print("Предупреждение: файл прочитан с заменой ошибок", file=sys.stderr)
        except Exception as e:
            print(f"Ошибка при чтении файла {filepath}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Исправляем кодировку текста из командной строки Windows
    if sys.platform == 'win32':
        try:
            # Если текст выглядит как неправильно декодированный UTF-8
            # (например, "РїСЂРёРІРµС‚" вместо "привет")
            # Пробуем исправить: кодируем в latin-1 и декодируем из cp1251
            if isinstance(text, str):
                # Проверяем, есть ли признаки неправильной кодировки
                try:
                    # Пробуем закодировать в latin-1 (это всегда работает для байтов 0-255)
                    text_bytes = text.encode('latin-1')
                    # Декодируем из cp1251 (Windows кодировка)
                    text = text_bytes.decode('cp1251')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    # Если не получилось, пробуем другой способ
                    try:
                        # Может быть текст уже в UTF-8, но был неправильно интерпретирован
                        text_bytes = text.encode('cp1251', errors='ignore')
                        text = text_bytes.decode('utf-8', errors='ignore')
                    except:
                        pass
        except Exception as e:
            print(f"Предупреждение при исправлении кодировки: {e}", file=sys.stderr)
    
    if not text:
        print("Ошибка: текст для озвучивания не указан", file=sys.stderr)
        sys.exit(1)
    
    # Запоминаем время перед созданием файла
    before_time = time.time()
    
    # Запускаем text_to_speech.py
    # Используем stdin для передачи текста, чтобы избежать проблем с кодировкой
    try:
        # Отладочный вывод
        print(f"Передаваемый текст: '{text}'", file=sys.stderr)
        print(f"Длина текста: {len(text)} символов", file=sys.stderr)
        print(f"Кодировка текста: {text.encode('utf-8')}", file=sys.stderr)
        
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
        
        # Выводим stderr для отладки
        if stderr:
            print(stderr, file=sys.stderr)
        
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

