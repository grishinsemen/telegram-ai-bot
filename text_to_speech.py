#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для преобразования текста в речь через MiniMax API
"""

import requests
import json
import sys
import os
import glob
import io
import re

# Устанавливаем UTF-8 для вывода в Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Получаем API ключ из конфигурации или переменной окружения
def get_api_key():
    # Сначала пробуем из переменной окружения
    api_key = os.getenv('MINIMAX_API_KEY')
    
    if not api_key:
        # Сначала пробуем локальный файл mcp.json в папке проекта
        local_config = "mcp.json"
        config_path = None
        
        if os.path.exists(local_config):
            config_path = local_config
        else:
            # Если локального нет, пробуем системный файл Cursor
            config_path = os.path.expanduser(
                r'%APPDATA%\Cursor\User\globalStorage\mcp.json'
            )
            config_path = os.path.expandvars(config_path)
        
        if os.path.exists(config_path):
            try:
                # Пробуем разные кодировки
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
        print("Ошибка: API ключ не найден. Убедитесь, что он настроен в конфигурации MCP.", file=sys.stderr)
        sys.exit(1)
    
    return api_key

def load_tts_config():
    """Загружает настройки из файла конфигурации"""
    config_file = "tts_config.json"
    default_config = {
        "model": "speech-2.6-hd",
        "voice_setting": {
            "voice_id": "moss_audio_3c5cbd6d-c6e0-11f0-a49b-b65555212881",
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
        },
        "stream": False
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Объединяем с дефолтными настройками
                config = default_config.copy()
                config.update(user_config)
                # Обновляем вложенные словари
                if 'voice_setting' in user_config:
                    config['voice_setting'].update(user_config['voice_setting'])
                if 'audio_setting' in user_config:
                    config['audio_setting'].update(user_config['audio_setting'])
                return config
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}. Используются настройки по умолчанию.", file=sys.stderr)
    
    return default_config

def text_to_speech(text, api_key, voice_id=None, speed=None, volume=None):
    """
    Преобразует текст в речь через MiniMax T2A API
    Использует настройки из tts_config.json или параметры по умолчанию
    """
    # Загружаем настройки из конфигурации
    config = load_tts_config()
    
    url = "https://api.minimax.io/v1/t2a_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Используем параметры из конфигурации, если не переданы явно
    voice_setting = config['voice_setting'].copy()
    if voice_id:
        voice_setting['voice_id'] = voice_id
    if speed is not None:
        voice_setting['speed'] = speed
    if volume is not None:
        voice_setting['vol'] = volume
    
    # Убеждаемся, что текст в UTF-8 и правильно обработан
    if isinstance(text, str):
        # Нормализуем текст - убеждаемся, что он в правильной кодировке
        try:
            # Проверяем, что текст уже в UTF-8
            text.encode('utf-8')
            text_utf8 = text
        except UnicodeEncodeError:
            # Если не получается закодировать, пробуем исправить
            try:
                # Пробуем декодировать как cp1251 и перекодировать в UTF-8
                text_bytes = text.encode('latin-1', errors='ignore')
                text_utf8 = text_bytes.decode('cp1251', errors='ignore')
            except:
                text_utf8 = text
    else:
        text_utf8 = str(text)
    
    # Удаляем кавычки из текста (решает проблемы с PowerShell при длинных текстах)
    # Заменяем все виды кавычек на пробелы
    text_utf8 = re.sub(r'["""''«»]', ' ', text_utf8)  # Удаляем все виды кавычек
    text_utf8 = re.sub(r'\s+', ' ', text_utf8)  # Убираем множественные пробелы
    text_utf8 = text_utf8.strip()
    
    # Отладочный вывод для проверки текста
    print(f"Отправляемый текст (UTF-8): '{text_utf8}'", file=sys.stderr)
    print(f"Длина текста: {len(text_utf8)} символов", file=sys.stderr)
    
    payload = {
        "model": config['model'],
        "text": text_utf8,
        "stream": config.get('stream', False),
        "voice_setting": voice_setting,
        "audio_setting": config['audio_setting'].copy()
    }
    
    # Добавляем language_boost если указан в конфигурации
    if 'language_boost' in config:
        payload['language_boost'] = config['language_boost']
    
    # Убеждаемся, что JSON сериализуется с правильной кодировкой
    try:
        # Проверяем, что payload правильно сериализуется
        json_payload = json.dumps(payload, ensure_ascii=False)
        response = requests.post(url, headers=headers, data=json_payload.encode('utf-8'), timeout=30)
        response.raise_for_status()
        
        # MiniMax API возвращает аудио в hex формате
        result = response.json()
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}", file=sys.stderr)
        raise

def main():
    # Устанавливаем кодировку для stdin (если нужно)
    if sys.platform == 'win32':
        if hasattr(sys.stdin, 'buffer'):
            sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        # Если аргументов нет, пробуем прочитать из stdin
        if not sys.stdin.isatty():
            # Читаем из stdin с правильной кодировкой
            # В Windows при чтении через pipe может быть проблема с кодировкой
            if sys.platform == 'win32' and hasattr(sys.stdin, 'buffer'):
                # Читаем байты напрямую и декодируем
                try:
                    raw_bytes = sys.stdin.buffer.read()
                    # Пробуем разные кодировки
                    text_decoded = False
                    for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
                        try:
                            decoded_text = raw_bytes.decode(encoding).strip()
                            # Проверяем, что текст содержит кириллицу (признак правильной декодировки)
                            cyrillic_count = sum(1 for c in decoded_text if '\u0400' <= c <= '\u04FF')
                            if cyrillic_count > 5:  # Должно быть достаточно кириллицы
                                text = decoded_text
                                text_decoded = True
                                print(f"Текст прочитан с кодировкой: {encoding}, кириллических символов: {cyrillic_count}", file=sys.stderr)
                                break
                        except (UnicodeDecodeError, UnicodeError):
                            continue
                    
                    if not text_decoded:
                        # Если ничего не подошло, используем utf-8 с заменой ошибок
                        text = raw_bytes.decode('utf-8', errors='replace').strip()
                        print("Предупреждение: текст прочитан с заменой ошибок", file=sys.stderr)
                except Exception as e:
                    # Fallback на обычное чтение
                    print(f"Ошибка при чтении из stdin: {e}, используем обычное чтение", file=sys.stderr)
                    text = sys.stdin.read().strip()
            else:
                text = sys.stdin.read().strip()
            
            # Убираем BOM если есть
            if text.startswith('\ufeff'):
                text = text[1:]
        else:
            text = "Привет, это тест MiniMax"
    else:
        text = sys.argv[1]
        # В Windows текст из командной строки может приходить в cp1251
        # Пробуем исправить кодировку
        if sys.platform == 'win32':
            try:
                # Если текст выглядит как неправильно декодированный UTF-8 (кракозябры)
                # Пробуем перекодировать через cp1251 -> utf-8
                if isinstance(text, str):
                    # Проверяем, есть ли кириллица в неправильной кодировке
                    # Если текст содержит символы типа 'РїСЂРёРІРµС‚', это cp1251, декодированная как latin-1
                    try:
                        # Пробуем закодировать в cp1251 и декодировать в utf-8
                        text_bytes = text.encode('latin-1')
                        text = text_bytes.decode('cp1251')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        # Если не получилось, пробуем другой способ
                        try:
                            text_bytes = text.encode('cp1251')
                            text = text_bytes.decode('utf-8')
                        except:
                            pass
            except:
                pass
    
    print(f"Преобразую текст в речь: '{text}'", file=sys.stderr)
    print("Загрузка...", file=sys.stderr)
    
    try:
        api_key = get_api_key()
        result = text_to_speech(text, api_key)
        
        # Результат будет сохранен в функции text_to_speech
        
        # MiniMax возвращает аудио в hex формате в data.audio
        if 'data' in result and 'audio' in result['data']:
            print("Аудио данные получены (hex)", file=sys.stderr)
            # Декодируем из hex
            audio_hex = result['data']['audio']
            audio_data = bytes.fromhex(audio_hex)
            
            # Создаем папку audio если её нет
            audio_dir = "audio"
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            
            # Находим следующий доступный номер для файла
            existing_files = glob.glob(f"{audio_dir}/*.mp3")
            if existing_files:
                # Извлекаем номера из существующих файлов
                numbers = []
                for file in existing_files:
                    basename = os.path.basename(file)
                    # Пробуем извлечь число из имени файла (например, "1.mp3" -> 1)
                    try:
                        num = int(os.path.splitext(basename)[0])
                        numbers.append(num)
                    except ValueError:
                        # Если не число, пропускаем
                        continue
                # Находим следующий номер
                next_num = max(numbers) + 1 if numbers else 1
            else:
                next_num = 1
            
            # Генерируем имя файла с простой нумерацией
            audio_filename = f"{audio_dir}/{next_num}.mp3"
            json_filename = f"{audio_dir}/{next_num}.json"
            
            # Сохраняем аудио
            with open(audio_filename, "wb") as f:
                f.write(audio_data)
            print(f"Аудио файл сохранен: {audio_filename}", file=sys.stderr)
            
            # Выводим путь к файлу в stdout для автоматического открытия
            print(f"AUDIO_FILE:{audio_filename}", file=sys.stdout)
            
            # Сохраняем JSON с метаданными
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Метаданные сохранены: {json_filename}", file=sys.stderr)
        elif 'audio_url' in result:
            print(f"Аудио URL: {result['audio_url']}", file=sys.stderr)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

