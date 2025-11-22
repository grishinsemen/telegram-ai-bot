#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот, который автоматически отвечает голосовыми сообщениями
когда его цитируют или задают вопрос
Оптимизированная версия с рефакторингом
"""

import json
import sys
import os
import subprocess
import time
import glob
import requests
import io
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, List, Tuple

# Устанавливаем UTF-8 для вывода в Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Константы
GROUP_CONTEXT = """В беседе вас четверо: Алексей Тарасов, Алексей Корабейник, Михаил и Семён. Вы увлекаетесь музыкой и у вас своя небольшая группа "Сустейн".

Состав группы:
- Тарасов - на барабанах
- Семён Гришин - бас
- Корабейник - соло гитара
- Михаил - баян

Вы часто собираетесь в Мелихово на репетицию, это в Подмосковье. Там дом с тёплым, баня есть, пиво можно выпить."""
MAX_TOKENS = 300
TEMPERATURE = 0.7
AUDIO_MAX_FILES = 50
LAST_UPDATE_ID_FILE = "last_update_id.txt"

class BotConfig:
    """Класс для хранения конфигурации бота"""
    def __init__(self, config_dict: dict):
        self.bot_token = config_dict.get('bot_token')
        self.chat_id = config_dict.get('chat_id')
        self.personality = config_dict.get('personality', 'default')
        
        # ZenMux
        self.zenmux_api_key = config_dict.get('zenmux_api_key')
        self.zenmux_model = config_dict.get('zenmux_model', 'google/gemini-3-pro-preview-free')
        self.zenmux_base_url = config_dict.get('zenmux_base_url', 'https://zenmux.ai/api/v1')
        self.fallback_models = config_dict.get('fallback_models', [])
        
        # OpenRouter
        self.openrouter_api_key = config_dict.get('openrouter_api_key')
        self.openrouter_model = config_dict.get('openrouter_model', 'openai/gpt-4o-mini')
        
        # OpenAI
        self.openai_api_key = config_dict.get('openai_api_key')
        self.openai_model = config_dict.get('openai_model', 'gpt-4o-mini')
        
        # Groq
        self.groq_api_key = config_dict.get('groq_api_key')
        self.groq_model = config_dict.get('groq_model', 'llama-3.3-70b-versatile')
        
        # Transcription services
        self.assemblyai_api_key = config_dict.get('assemblyai_api_key')
        self.deepgram_api_key = config_dict.get('deepgram_api_key')
        self.lemonfox_api_key = config_dict.get('lemonfox_api_key')
    
    def has_zenmux(self) -> bool:
        return bool(self.zenmux_api_key and self.zenmux_api_key != "YOUR_ZENMUX_API_KEY_HERE")
    
    def has_openrouter(self) -> bool:
        return bool(self.openrouter_api_key and self.openrouter_api_key != "YOUR_OPENROUTER_API_KEY_HERE")
    
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key != "YOUR_OPENAI_API_KEY_HERE")
    
    def has_groq(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key != "YOUR_GROQ_API_KEY_HERE")
    
    def has_any_api(self) -> bool:
        return self.has_zenmux() or self.has_openrouter() or self.has_openai() or self.has_groq()
    
    def has_assemblyai(self) -> bool:
        return bool(self.assemblyai_api_key and self.assemblyai_api_key != "YOUR_ASSEMBLYAI_API_KEY_HERE")
    
    def has_deepgram(self) -> bool:
        return bool(self.deepgram_api_key and self.deepgram_api_key != "YOUR_DEEPGRAM_API_KEY_HERE")
    
    def has_lemonfox(self) -> bool:
        return bool(self.lemonfox_api_key and self.lemonfox_api_key != "YOUR_LEMONFOX_API_KEY_HERE")

@lru_cache(maxsize=10)
def get_personality_prompt(personality="default"):
    """Возвращает описание личности для промпта (кэшируется)"""
    personalities = {
        "putin": """Ты - Владимир Владимирович Путин, Президент Российской Федерации. 
Отвечай в его стиле: спокойно, уверенно, сдержанно, иногда с легкой иронией. 
Используй характерные выражения и манеру речи. Отвечай по делу, как на пресс-конференции или в неформальной беседе.
Не переигрывай, будь естественным. Отвечай на русском языке.""",
        
        "default": """Ты - дружелюбный бот в групповом чате. Отвечай кратко, естественно и по делу.
Будь живым и интересным собеседником.""",
        
        "friendly": """Ты - очень дружелюбный и общительный бот. Отвечай тепло, с энтузиазмом, используй эмодзи в мыслях.
Будь позитивным и поддерживающим собеседником.""",
        
        "professional": """Ты - профессиональный и вежливый бот. Отвечай формально, но дружелюбно.
Используй деловой стиль общения, будь точным и информативным.""",
        
        "funny": """Ты - веселый и остроумный бот с чувством юмора. Отвечай с шутками, иронией и сарказмом.
Будь забавным, но не переходи границы. Используй мемы и отсылки в разумных пределах."""
    }
    
    return personalities.get(personality, personality)

def build_prompt(text: str, personality: str) -> str:
    """Строит промпт для AI (кэшируется через get_personality_prompt)"""
    personality_desc = get_personality_prompt(personality)
    return f"""{personality_desc}

Контекст: тебе написали в групповом чате.
{GROUP_CONTEXT}
Сообщение: {text}

Ответь на это сообщение естественно, как в обычном разговоре."""

def generate_response_with_provider(
    text: str,
    provider_config: Dict,
    session: requests.Session,
    personality: str
) -> Optional[str]:
    """
    Универсальная функция для генерации ответа через любой AI провайдер
    provider_config должен содержать: url, api_key, model, headers (опционально)
    """
    if not provider_config.get('api_key') or provider_config['api_key'].startswith('YOUR_'):
        return None
    
    url = provider_config['url']
    api_key = provider_config['api_key']
    model = provider_config['model']
    custom_headers = provider_config.get('headers', {})
    
    prompt = build_prompt(text, personality)
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **custom_headers
    }
    
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                content = message.get('content', '')
                # Для ZenMux: проверяем reasoning если content пустой
                if not content and 'reasoning' in message:
                    content = message.get('reasoning', '')
                if content:
                    return content.strip()
        elif response.status_code == 429:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {provider_config.get('name', 'API')} ({model}): Превышен лимит запросов (429)", file=sys.stderr)
        else:
            error_text = response.text[:200] if hasattr(response, 'text') else str(response.status_code)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка {provider_config.get('name', 'API')} ({model}) {response.status_code}: {error_text}", file=sys.stderr)
            
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Таймаут при обращении к {provider_config.get('name', 'API')} ({model})", file=sys.stderr)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при вызове {provider_config.get('name', 'API')} ({model}): {e}", file=sys.stderr)
    
    return None

def generate_response(text: str, config: BotConfig, session: requests.Session) -> Optional[str]:
    """
    Генерирует ответ используя провайдеры в порядке приоритета:
    ZenMux (основная + запасные модели) -> OpenRouter -> OpenAI -> Groq
    """
    # Пробуем ZenMux
    if config.has_zenmux():
        models_to_try = [config.zenmux_model]
        if config.fallback_models:
            models_to_try.extend([m for m in config.fallback_models if m not in models_to_try])
        else:
            fallback = "google/gemini-3-pro-preview"
            if fallback not in models_to_try:
                models_to_try.append(fallback)
        
        for i, model in enumerate(models_to_try):
            if i == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Пробую основную модель ZenMux: {model}", file=sys.stderr)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Модель ZenMux {i} не ответила, пробую следующую: {model}", file=sys.stderr)
            
            provider_config = {
                'name': 'ZenMux',
                'url': f"{config.zenmux_base_url}/chat/completions",
                'api_key': config.zenmux_api_key,
                'model': model
            }
            
            response = generate_response_with_provider(text, provider_config, session, config.personality)
            if response:
                if i > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Модель ZenMux {model} сработала!", file=sys.stderr)
                return response
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Все модели ZenMux не ответили", file=sys.stderr)
    
    # Пробуем OpenRouter
    if config.has_openrouter():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 ZenMux не ответил, пробую OpenRouter: {config.openrouter_model}", file=sys.stderr)
        provider_config = {
            'name': 'OpenRouter',
            'url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_key': config.openrouter_api_key,
            'model': config.openrouter_model,
            'headers': {
                'HTTP-Referer': 'https://github.com/telegram-bot',
                'X-Title': 'Telegram Bot'
            }
        }
        response = generate_response_with_provider(text, provider_config, session, config.personality)
        if response:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ OpenRouter сработал!", file=sys.stderr)
            return response
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ OpenRouter тоже не ответил", file=sys.stderr)
    
    # Пробуем OpenAI
    if config.has_openai():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 OpenRouter не ответил, пробую OpenAI: {config.openai_model}", file=sys.stderr)
        provider_config = {
            'name': 'OpenAI',
            'url': 'https://api.openai.com/v1/chat/completions',
            'api_key': config.openai_api_key,
            'model': config.openai_model
        }
        response = generate_response_with_provider(text, provider_config, session, config.personality)
        if response:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ OpenAI сработал!", file=sys.stderr)
            return response
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ OpenAI тоже не ответил", file=sys.stderr)
    
    # Пробуем Groq
    if config.has_groq():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 OpenAI не ответил, пробую Groq: {config.groq_model}", file=sys.stderr)
        provider_config = {
            'name': 'Groq',
            'url': 'https://api.groq.com/openai/v1/chat/completions',
            'api_key': config.groq_api_key,
            'model': config.groq_model
        }
        response = generate_response_with_provider(text, provider_config, session, config.personality)
        if response:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Groq сработал!", file=sys.stderr)
            return response
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Groq тоже не ответил", file=sys.stderr)
    
    return None

def cleanup_old_audio_files(max_files: int = AUDIO_MAX_FILES):
    """Удаляет старые аудиофайлы из папки audio, если их больше max_files"""
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        return
    
    mp3_files = glob.glob(f"{audio_dir}/*.mp3")
    if len(mp3_files) <= max_files:
        return
    
    mp3_files.sort(key=os.path.getmtime)
    files_to_delete = mp3_files[:-max_files]
    deleted_count = 0
    
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            deleted_count += 1
            json_path = os.path.splitext(file_path)[0] + ".json"
            if os.path.exists(json_path):
                os.remove(json_path)
        except Exception as e:
            print(f"Ошибка при удалении файла {file_path}: {e}", file=sys.stderr)
    
    if deleted_count > 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️ Удалено {deleted_count} старых аудиофайлов (было {len(mp3_files)}, осталось {max_files})", file=sys.stderr)

def cleanup_temp_voice_files():
    """Удаляет старые временные голосовые файлы (старше 1 часа)"""
    temp_dir = "temp_voice"
    if not os.path.exists(temp_dir):
        return
    
    current_time = time.time()
    deleted_count = 0
    
    for file_path in glob.glob(f"{temp_dir}/*"):
        try:
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > 3600:  # Удаляем файлы старше 1 часа
                os.remove(file_path)
                deleted_count += 1
        except Exception as e:
            print(f"Ошибка при удалении временного файла {file_path}: {e}", file=sys.stderr)
    
    if deleted_count > 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️ Удалено {deleted_count} старых временных голосовых файлов", file=sys.stderr)

def generate_audio(text: str) -> Optional[str]:
    """Генерирует аудио через text_to_speech.py"""
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
        
        audio_file = None
        for line in stdout.split('\n'):
            if line.startswith('AUDIO_FILE:'):
                audio_file = line.split('AUDIO_FILE:', 1)[1].strip()
                break
        
        if not audio_file:
            time.sleep(0.5)
            audio_dir = "audio"
            if os.path.exists(audio_dir):
                mp3_files = glob.glob(f"{audio_dir}/*.mp3")
                if mp3_files:
                    latest_file = max(mp3_files, key=os.path.getmtime)
                    if os.path.getmtime(latest_file) >= before_time:
                        audio_file = latest_file
        
        if audio_file and os.path.exists(audio_file):
            cleanup_old_audio_files()
            return audio_file
        
        return None
        
    except Exception as e:
        print(f"Ошибка при генерации аудио: {e}", file=sys.stderr)
        return None

def convert_mp3_to_ogg(mp3_path: str) -> str:
    """Конвертирует MP3 в OGG для Telegram (если нужно)"""
    ogg_path = mp3_path.replace('.mp3', '.ogg')
    
    try:
        subprocess.run(['ffmpeg', '-version'], 
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE, 
                     timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ FFmpeg не найден, отправляю MP3 напрямую", file=sys.stderr)
        return mp3_path
    
    try:
        subprocess.run([
            'ffmpeg', '-i', mp3_path, 
            '-acodec', 'libopus', 
            '-b:a', '64k',
            ogg_path,
            '-y'
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        return ogg_path
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ошибка при конвертации в OGG: {e}, отправляю MP3", file=sys.stderr)
        return mp3_path

def send_voice_message(bot_token: str, chat_id: str, audio_path: str, session: requests.Session) -> bool:
    """Отправляет голосовое сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendVoice"
    audio_path = convert_mp3_to_ogg(audio_path)
    
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {'voice': audio_file}
            data = {'chat_id': chat_id}
            response = session.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                return True
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка Telegram API: {result.get('description')}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при отправке: {e}", file=sys.stderr)
        return False

def should_respond(message: dict, bot_username: Optional[str] = None) -> bool:
    """Определяет, должен ли бот ответить на сообщение"""
    # Проверяем reply на сообщение бота
    if message.get('reply_to_message'):
        reply = message['reply_to_message']
        reply_from = reply.get('from', {})
        if reply_from.get('is_bot'):
            if not bot_username or reply_from.get('username') == bot_username:
                return True
    
    text = message.get('text', '') or message.get('caption', '')
    
    # Если это было голосовое сообщение (помечено после транскрипции) - всегда отвечаем
    if message.get('_was_voice'):
        return True
    
    # Если нет текста, но есть голосовое сообщение - нужно транскрибировать сначала
    # (это обрабатывается в process_updates до вызова should_respond)
    # После транскрипции текст будет в message['text'], и мы проверим его ниже
    if not text and (message.get('voice') or message.get('audio')):
        # Если голосовое сообщение - это reply на бота, то обрабатываем
        if message.get('reply_to_message'):
            reply = message['reply_to_message']
            reply_from = reply.get('from', {})
            if reply_from.get('is_bot'):
                if not bot_username or reply_from.get('username') == bot_username:
                    return True
        # Для остальных голосовых сообщений - транскрибируем и проверим текст после
        # Возвращаем True, чтобы транскрибировать, а потом проверим транскрибированный текст
        return True
    
    # Проверяем упоминание бота
    if text and bot_username and f'@{bot_username}' in text:
        return True
    
    # Проверяем текст на вопросы и обращения
    if text:
        text_lower = text.lower()
        if '?' in text:
            return True
        if any(word in text_lower for word in ['бот', 'помоги', 'расскажи', 'объясни', 'скажи']):
            return True
    
    return False

def download_voice_file(bot_token: str, file_id: str, session: requests.Session) -> Optional[str]:
    """Скачивает голосовой файл из Telegram и возвращает путь к файлу"""
    # Получаем информацию о файле
    get_file_url = f"https://api.telegram.org/bot{bot_token}/getFile"
    try:
        response = session.get(get_file_url, params={'file_id': file_id}, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if not result.get('ok'):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при получении информации о файле: {result.get('description')}", file=sys.stderr)
            return None
        
        file_path = result['result'].get('file_path')
        if not file_path:
            return None
        
        # Скачиваем файл
        file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        download_response = session.get(file_url, timeout=60)
        download_response.raise_for_status()
        
        # Сохраняем во временную папку
        temp_dir = "temp_voice"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Определяем расширение файла
        ext = os.path.splitext(file_path)[1] or '.ogg'
        temp_file = os.path.join(temp_dir, f"voice_{int(time.time())}{ext}")
        
        with open(temp_file, 'wb') as f:
            f.write(download_response.content)
        
        return temp_file
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при скачивании голосового файла: {e}", file=sys.stderr)
        return None

def transcribe_voice_with_huggingface(audio_file_path: str, session: requests.Session, api_key: Optional[str] = None) -> Optional[str]:
    """Транскрибирует голосовое сообщение через Hugging Face Inference API (бесплатно)"""
    # Пробуем разные модели Whisper в порядке приоритета
    models = [
        "openai/whisper-medium",  # Средняя модель, обычно доступна
        "openai/whisper-base",    # Базовая модель
        "openai/whisper-small",   # Малая модель
        "openai/whisper-tiny",    # Минимальная модель
        "jonatasgrosman/whisper-large-v2-russian",  # Специальная модель для русского
    ]
    
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    for model in models:
        url = f"https://api-inference.huggingface.co/models/{model}"
        
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ Пробую модель: {model}", file=sys.stderr)
            
            with open(audio_file_path, 'rb') as audio_file:
                response = session.post(
                    url,
                    files={'file': audio_file},
                    data={'language': 'russian'},  # Указываем русский язык
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 503:
                    # Модель загружается, ждем немного
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Модель {model} загружается, жду...", file=sys.stderr)
                    time.sleep(10)  # Увеличиваем время ожидания
                    # Повторяем запрос
                    audio_file.seek(0)
                    response = session.post(
                        url,
                        files={'file': audio_file},
                        data={'language': 'russian'},
                        headers=headers,
                        timeout=60
                    )
                
                if response.status_code == 410:
                    # Модель недоступна, пробуем следующую
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Модель {model} недоступна (410), пробую следующую...", file=sys.stderr)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                # Hugging Face Whisper возвращает словарь с полем 'text'
                # Формат: {"text": "транскрибированный текст"}
                if isinstance(result, dict):
                    text = result.get('text', '')
                    if not text and 'chunks' in result:
                        # Иногда возвращается в chunks
                        chunks = result.get('chunks', [])
                        if chunks and isinstance(chunks, list):
                            text = ' '.join([chunk.get('text', '') for chunk in chunks if isinstance(chunk, dict)])
                    text = text.strip()
                elif isinstance(result, str):
                    text = result.strip()
                elif isinstance(result, list) and len(result) > 0:
                    # Иногда возвращается список словарей
                    first_item = result[0]
                    if isinstance(first_item, dict):
                        text = first_item.get('text', '').strip()
                    else:
                        text = str(first_item).strip()
                else:
                    text = str(result).strip()
                
                if text:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Успешно транскрибировано через {model}", file=sys.stderr)
                    return text
                
        except requests.exceptions.HTTPError as e:
            if e.response:
                status_code = e.response.status_code
                if status_code == 410:
                    # Модель недоступна, пробуем следующую
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Модель {model} недоступна (410), пробую следующую...", file=sys.stderr)
                    continue
                elif status_code == 503:
                    # Модель загружается, пробуем следующую (или подождем)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Модель {model} загружается (503), пробую следующую...", file=sys.stderr)
                    continue
                else:
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get('error', '')
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ошибка {model}: {error_msg} ({status_code}), пробую следующую...", file=sys.stderr)
                    except:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ошибка {model}: {status_code}, пробую следующую...", file=sys.stderr)
                    continue
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ошибка {model}: {e}, пробую следующую...", file=sys.stderr)
                continue
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ошибка {model}: {e}, пробую следующую...", file=sys.stderr)
            continue
    
    # Если все модели не сработали
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Все модели Hugging Face недоступны", file=sys.stderr)
    return None

def transcribe_voice_with_openai(audio_file_path: str, api_key: str, session: requests.Session) -> Optional[str]:
    """Транскрибирует голосовое сообщение через OpenAI Whisper API"""
    url = "https://api.openai.com/v1/audio/transcriptions"
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {
                'model': 'whisper-1',
                'language': 'ru'  # Указываем русский язык для лучшей точности
            }
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            
            response = session.post(url, files=files, data=data, headers=headers, timeout=60)
            
            if response.status_code == 403:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', '')
                if 'unsupported_country' in error_msg.lower() or 'country' in error_msg.lower():
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ OpenAI API недоступен в вашем регионе (403)", file=sys.stderr)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}]    Пробую альтернативный сервис...", file=sys.stderr)
                    return None
            
            response.raise_for_status()
            result = response.json()
            
            text = result.get('text', '').strip()
            if text:
                return text
            return None
            
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 403:
            error_data = e.response.json() if e.response.content else {}
            error_msg = error_data.get('error', {}).get('message', '')
            if 'unsupported_country' in error_msg.lower() or 'country' in error_msg.lower():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ OpenAI API недоступен в вашем регионе (403)", file=sys.stderr)
                print(f"[{datetime.now().strftime('%H:%M:%S')}]    Пробую альтернативный сервис...", file=sys.stderr)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при транскрипции (403): {error_msg}", file=sys.stderr)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при транскрипции: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при транскрипции: {e}", file=sys.stderr)
        return None

def transcribe_voice_with_assemblyai(audio_file_path: str, api_key: str, session: requests.Session) -> Optional[str]:
    """Транскрибирует голосовое сообщение через AssemblyAI"""
    # Сначала загружаем файл
    upload_url = "https://api.assemblyai.com/v2/upload"
    headers = {"authorization": api_key}
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            upload_response = session.post(upload_url, headers=headers, files={"file": audio_file}, timeout=60)
            upload_response.raise_for_status()
            upload_data = upload_response.json()
            audio_url = upload_data.get('upload_url')
            
            if not audio_url:
                return None
            
            # Запрашиваем транскрипцию
            transcript_url = "https://api.assemblyai.com/v2/transcript"
            transcript_data = {
                "audio_url": audio_url,
                "language_code": "ru"  # Русский язык
            }
            
            transcript_response = session.post(transcript_url, json=transcript_data, headers=headers, timeout=60)
            transcript_response.raise_for_status()
            transcript_data = transcript_response.json()
            transcript_id = transcript_data.get('id')
            
            if not transcript_id:
                return None
            
            # Ждем завершения транскрипции (polling)
            polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
            max_attempts = 30
            for attempt in range(max_attempts):
                polling_response = session.get(polling_url, headers=headers, timeout=60)
                polling_response.raise_for_status()
                polling_data = polling_response.json()
                
                status = polling_data.get('status')
                if status == 'completed':
                    text = polling_data.get('text', '').strip()
                    if text:
                        return text
                    return None
                elif status == 'error':
                    error = polling_data.get('error', 'Unknown error')
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ AssemblyAI ошибка: {error}", file=sys.stderr)
                    return None
                
                time.sleep(1)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ AssemblyAI: таймаут ожидания транскрипции", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка AssemblyAI: {e}", file=sys.stderr)
        return None

def transcribe_voice_with_deepgram(audio_file_path: str, api_key: str, session: requests.Session) -> Optional[str]:
    """Транскрибирует голосовое сообщение через Deepgram"""
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {api_key}"
    }
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            params = {
                "language": "ru",  # Русский язык
                "model": "nova-2",  # Лучшая модель для точности
                "punctuate": "true"
            }
            
            response = session.post(url, headers=headers, files={"file": audio_file}, data=params, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Deepgram возвращает результат в формате {"results": {"channels": [{"alternatives": [{"transcript": "..."}]}]}]}
            channels = result.get('results', {}).get('channels', [])
            if channels and len(channels) > 0:
                alternatives = channels[0].get('alternatives', [])
                if alternatives and len(alternatives) > 0:
                    text = alternatives[0].get('transcript', '').strip()
                    if text:
                        return text
            
            return None
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка Deepgram: {e}", file=sys.stderr)
        return None

def transcribe_voice_with_lemonfox(audio_file_path: str, api_key: str, session: requests.Session) -> Optional[str]:
    """Транскрибирует голосовое сообщение через Lemonfox.ai Whisper API"""
    url = "https://api.lemonfox.ai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {
                'model': 'whisper-1',
                'language': 'ru'  # Русский язык
            }
            
            response = session.post(url, files=files, data=data, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            text = result.get('text', '').strip()
            if text:
                return text
            return None
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка Lemonfox: {e}", file=sys.stderr)
        return None

def transcribe_voice(audio_file_path: str, config: BotConfig, session: requests.Session) -> Optional[str]:
    """Транскрибирует голосовое сообщение, пробуя разные сервисы в порядке приоритета"""
    # 1. Пробуем OpenAI (если доступен)
    if config.has_openai():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ Пробую транскрипцию через OpenAI Whisper...", file=sys.stderr)
        result = transcribe_voice_with_openai(audio_file_path, config.openai_api_key, session)
        if result:
            return result
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ OpenAI не сработал, пробую альтернативный сервис...", file=sys.stderr)
    
    # 2. Пробуем AssemblyAI (если есть ключ)
    if config.has_assemblyai():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ Пробую транскрипцию через AssemblyAI...", file=sys.stderr)
        result = transcribe_voice_with_assemblyai(audio_file_path, config.assemblyai_api_key, session)
        if result:
            return result
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ AssemblyAI не сработал, пробую следующий сервис...", file=sys.stderr)
    
    # 3. Пробуем Deepgram (если есть ключ)
    if config.has_deepgram():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ Пробую транскрипцию через Deepgram...", file=sys.stderr)
        result = transcribe_voice_with_deepgram(audio_file_path, config.deepgram_api_key, session)
        if result:
            return result
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Deepgram не сработал, пробую следующий сервис...", file=sys.stderr)
    
    # 4. Пробуем Lemonfox.ai (если есть ключ)
    if config.has_lemonfox():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ Пробую транскрипцию через Lemonfox.ai...", file=sys.stderr)
        result = transcribe_voice_with_lemonfox(audio_file_path, config.lemonfox_api_key, session)
        if result:
            return result
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Lemonfox не сработал, пробую следующий сервис...", file=sys.stderr)
    
    # 5. Пробуем Hugging Face (бесплатно, без ключа)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ Пробую транскрипцию через Hugging Face (бесплатно)...", file=sys.stderr)
    result = transcribe_voice_with_huggingface(audio_file_path, session)
    if result:
        return result
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Не удалось транскрибировать через доступные сервисы", file=sys.stderr)
    return None

def get_bot_info(bot_token: str, session: requests.Session) -> Optional[dict]:
    """Получает информацию о боте"""
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            return result.get('result', {})
    except Exception as e:
        print(f"Ошибка при получении информации о боте: {e}", file=sys.stderr)
    return None

class UpdateManager:
    """Класс для управления last_update_id с оптимизацией записи"""
    def __init__(self, file_path: str = LAST_UPDATE_ID_FILE):
        self.file_path = file_path
        self.last_update_id = 0
        self.pending_write = False
        self.load()
    
    def load(self):
        """Загружает last_update_id из файла"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.last_update_id = int(f.read().strip())
            except:
                pass
    
    def update(self, update_id: int):
        """Обновляет last_update_id (записывает в файл только если изменился)"""
        if update_id > self.last_update_id:
            self.last_update_id = update_id
            try:
                with open(self.file_path, 'w') as f:
                    f.write(str(self.last_update_id))
            except Exception as e:
                print(f"Ошибка при записи last_update_id: {e}", file=sys.stderr)

def process_updates(config: BotConfig, bot_username: Optional[str], session: requests.Session):
    """Обрабатывает обновления от Telegram"""
    url = f"https://api.telegram.org/bot{config.bot_token}/getUpdates"
    update_manager = UpdateManager()
    
    try:
        params = {'offset': update_manager.last_update_id + 1, 'timeout': 30}
        response = session.get(url, params=params, timeout=35)
        response.raise_for_status()
        result = response.json()
        
        if not result.get('ok'):
            return
        
        for update in result.get('result', []):
            update_id = update.get('update_id')
            message = update.get('message')
            
            if not message:
                update_manager.update(update_id)
                continue
            
            msg_chat_id = str(message.get('chat', {}).get('id', ''))
            if msg_chat_id != str(config.chat_id):
                update_manager.update(update_id)
                continue
            
            update_manager.update(update_id)
            
            # Проверяем голосовое сообщение
            voice = message.get('voice')
            audio = message.get('audio')
            text = message.get('text', '') or message.get('caption', '')
            
            # Если есть голосовое сообщение, транскрибируем его СНАЧАЛА
            if voice or audio:
                file_id = voice.get('file_id') if voice else audio.get('file_id')
                if file_id:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎤 Получено голосовое сообщение, начинаю транскрипцию...", file=sys.stderr)
                    
                    # Скачиваем файл
                    voice_file = download_voice_file(config.bot_token, file_id, session)
                    if not voice_file:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Не удалось скачать голосовое сообщение", file=sys.stderr)
                        continue
                    
                    # Транскрибируем голосовое сообщение (пробуем разные сервисы)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎙️ Начинаю транскрипцию голосового сообщения...", file=sys.stderr)
                    transcribed_text = transcribe_voice(voice_file, config, session)
                    
                    # Удаляем временный файл
                    try:
                        os.remove(voice_file)
                    except:
                        pass
                    
                    if transcribed_text:
                        text = transcribed_text
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Транскрибировано: {text[:100]}...", file=sys.stderr)
                        # Обновляем сообщение с транскрибированным текстом для проверки should_respond
                        message['text'] = transcribed_text
                        # Помечаем, что это было голосовое сообщение (для should_respond)
                        message['_was_voice'] = True
                        # Удаляем voice/audio из сообщения, чтобы should_respond проверял только текст
                        if 'voice' in message:
                            del message['voice']
                        if 'audio' in message:
                            del message['audio']
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Не удалось транскрибировать голосовое сообщение", file=sys.stderr)
                        print(f"[{datetime.now().strftime('%H:%M:%S')}]    Попробуйте отправить текстовое сообщение", file=sys.stderr)
                        continue
            
            if text:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Новое сообщение в чате: {text[:100]}...", file=sys.stderr)
            
            # Проверяем, нужно ли отвечать (после транскрипции, если было голосовое)
            if not should_respond(message, bot_username):
                if text:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏭️ Пропускаю (не подходит под условия ответа)", file=sys.stderr)
                continue
            
            if not text:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Сообщение без текста - пропускаю", file=sys.stderr)
                continue
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ БОТ БУДЕТ ОТВЕЧАТЬ на сообщение: {text[:50]}...", file=sys.stderr)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Генерирую ответ через AI...", file=sys.stderr)
            response_text = generate_response(text, config, session)
            
            if not response_text:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ AI не смог сгенерировать ответ", file=sys.stderr)
                print(f"[{datetime.now().strftime('%H:%M:%S')}]    Возможные причины: превышен лимит запросов, ошибка API, или модель не ответила", file=sys.stderr)
                time.sleep(5)
                continue
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Ответ сгенерирован: {response_text[:50]}...", file=sys.stderr)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎤 Создаю голосовое сообщение...", file=sys.stderr)
            audio_file = generate_audio(response_text)
            if not audio_file:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Не удалось создать аудио", file=sys.stderr)
                continue
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📤 Отправляю голосовое сообщение...", file=sys.stderr)
            if send_voice_message(config.bot_token, config.chat_id, audio_file, session):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Голосовое сообщение успешно отправлено!", file=sys.stderr)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка при отправке голосового сообщения", file=sys.stderr)
            
            time.sleep(1)
        
    except requests.exceptions.Timeout:
        pass
    except Exception as e:
        print(f"Ошибка при обработке обновлений: {e}", file=sys.stderr)

def get_config() -> Optional[BotConfig]:
    """Получает конфигурацию"""
    config_file = "telegram_config.json"
    if not os.path.exists(config_file):
        print(f"Файл {config_file} не найден", file=sys.stderr)
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return BotConfig(config_dict)
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}", file=sys.stderr)
        return None

def main():
    config = get_config()
    if not config:
        sys.exit(1)
    
    if not config.bot_token or config.bot_token == "YOUR_BOT_TOKEN_HERE":
        print("Ошибка: bot_token не настроен", file=sys.stderr)
        sys.exit(1)
    
    if not config.chat_id or config.chat_id == "YOUR_CHAT_ID_HERE":
        print("Ошибка: chat_id не настроен", file=sys.stderr)
        sys.exit(1)
    
    # Создаем сессию для переиспользования соединений
    session = requests.Session()
    
    # Выводим красивый заголовок
    print("\n" + "=" * 60, file=sys.stderr)
    print("🤖 TELEGRAM БОТ ЗАПУЩЕН (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    print("\n📡 Статус подключений:", file=sys.stderr)
    if config.has_zenmux():
        print(f"   ✅ ZenMux.ai: подключен (основной)", file=sys.stderr)
        print(f"      Основная модель: {config.zenmux_model}", file=sys.stderr)
        if config.fallback_models:
            print(f"      Запасные модели ZenMux: {', '.join(config.fallback_models)}", file=sys.stderr)
    else:
        print("   ❌ ZenMux API ключ не настроен", file=sys.stderr)
    
    if config.has_openrouter():
        print(f"   ✅ OpenRouter: подключен (запасной #1)", file=sys.stderr)
        print(f"      Модель: {config.openrouter_model}", file=sys.stderr)
    else:
        print("   ⚠️ OpenRouter API ключ не настроен (запасной #1)", file=sys.stderr)
    
    if config.has_openai():
        print(f"   ✅ OpenAI: подключен (запасной #2)", file=sys.stderr)
        print(f"      Модель: {config.openai_model}", file=sys.stderr)
    else:
        print("   ⚠️ OpenAI API ключ не настроен (запасной #2)", file=sys.stderr)
    
    if config.has_groq():
        print(f"   ✅ Groq: подключен (запасной #3)", file=sys.stderr)
        print(f"      Модель: {config.groq_model}", file=sys.stderr)
    else:
        print("   ⚠️ Groq API ключ не настроен (запасной #3)", file=sys.stderr)
    
    if not config.has_any_api():
        print("\n   ❌ Нет ни одного API ключа - бот не будет отвечать", file=sys.stderr)
        print("      Добавьте хотя бы один API ключ в telegram_config.json", file=sys.stderr)
    
    personality_names = {
        "putin": "Владимир Путин",
        "default": "Обычный бот",
        "friendly": "Дружелюбный",
        "professional": "Профессиональный",
        "funny": "Веселый"
    }
    personality_display = personality_names.get(config.personality, f"Кастомная: {config.personality[:30]}")
    print(f"\n🎭 Личность бота: {personality_display}", file=sys.stderr)
    
    print("\n🔍 Проверка бота...", file=sys.stderr)
    bot_info = get_bot_info(config.bot_token, session)
    if bot_info:
        bot_username = bot_info.get('username')
        bot_name = bot_info.get('first_name', '')
        print(f"   ✅ Бот найден: @{bot_username} ({bot_name})", file=sys.stderr)
    else:
        bot_username = None
        print("   ❌ Не удалось получить информацию о боте", file=sys.stderr)
        print("      Проверьте правильность bot_token", file=sys.stderr)
    
    print(f"\n💬 Чат ID: {config.chat_id}", file=sys.stderr)
    
    print("\n" + "=" * 60, file=sys.stderr)
    print("📋 БОТ АКТИВЕН И СЛУШАЕТ СООБЩЕНИЯ", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("\n📝 Бот будет отвечать когда:", file=sys.stderr)
    print("   1. Его цитируют (reply на сообщение бота)", file=sys.stderr)
    print("   2. Его упоминают (@username)", file=sys.stderr)
    print("   3. Задают вопрос (есть '?')", file=sys.stderr)
    print("   4. Обращаются к боту (слова: бот, помоги, расскажи и т.д.)", file=sys.stderr)
    print("   5. Отправляют голосовое сообщение (требует OpenAI API ключ)", file=sys.stderr)
    
    if config.has_openai():
        print("\n🎤 Поддержка голосовых сообщений: ✅ Включена (OpenAI Whisper)", file=sys.stderr)
    else:
        print("\n🎤 Поддержка голосовых сообщений: ⚠️ Отключена (нужен OpenAI API ключ)", file=sys.stderr)
    print("\n⏳ Ожидание сообщений...", file=sys.stderr)
    print("   (Нажмите Ctrl+C для остановки)", file=sys.stderr)
    print("\n" + "-" * 60 + "\n", file=sys.stderr)
    
    try:
        while True:
            cleanup_temp_voice_files()  # Периодически очищаем временные файлы
            process_updates(config, bot_username, session)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60, file=sys.stderr)
        print("🛑 БОТ ОСТАНОВЛЕН ПОЛЬЗОВАТЕЛЕМ", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
    except Exception as e:
        print(f"\n\n[{datetime.now().strftime('%H:%M:%S')}] ❌ Критическая ошибка: {e}", file=sys.stderr)
        print("Бот остановлен из-за ошибки", file=sys.stderr)
    finally:
        session.close()

if __name__ == "__main__":
    main()
