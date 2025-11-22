import json
import sys
import os
from datetime import datetime

# Создаем папку audio если её нет
audio_dir = "audio"
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

# Ищем последний JSON файл в папке audio или текущей директории
json_files = []
if os.path.exists(audio_dir):
    json_files = [f for f in os.listdir(audio_dir) if f.endswith('.json')]
if not json_files:
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]

if not json_files:
    print("Не найден файл output_audio.json")
    sys.exit(1)

# Берем последний файл
latest_json = max(json_files, key=lambda f: os.path.getmtime(os.path.join(audio_dir, f) if os.path.exists(os.path.join(audio_dir, f)) else f))
json_path = os.path.join(audio_dir, latest_json) if os.path.exists(os.path.join(audio_dir, latest_json)) else latest_json

# Читаем результат из файла
with open(json_path, "r", encoding="utf-8") as f:
    result = json.load(f)

# Извлекаем аудио данные (hex формат)
audio_hex = result["data"]["audio"]

# Декодируем из hex в байты
audio_bytes = bytes.fromhex(audio_hex)

# Генерируем имя файла с timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
audio_filename = os.path.join(audio_dir, f"audio_{timestamp}.mp3")

# Сохраняем в MP3 файл
with open(audio_filename, "wb") as f:
    f.write(audio_bytes)

print(f"Аудио файл сохранен: {audio_filename}")
print(f"Размер: {len(audio_bytes)} байт")
print(f"Длительность: {result['extra_info']['audio_length'] / 1000:.2f} секунд")

