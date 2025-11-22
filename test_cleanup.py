# -*- coding: utf-8 -*-
"""Тест функции очистки аудиофайлов"""
import sys
import os
import glob

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from telegram_bot import cleanup_old_audio_files

def main():
    audio_dir = "audio"
    
    if not os.path.exists(audio_dir):
        print(f"Папка {audio_dir} не существует", file=sys.stderr)
        return
    
    mp3_files = glob.glob(f"{audio_dir}/*.mp3")
    print(f"Текущее количество файлов: {len(mp3_files)}", file=sys.stderr)
    
    if mp3_files:
        # Показываем самые старые и новые файлы
        mp3_files_sorted = sorted(mp3_files, key=os.path.getmtime)
        print(f"\nСамый старый файл: {os.path.basename(mp3_files_sorted[0])}", file=sys.stderr)
        print(f"Самый новый файл: {os.path.basename(mp3_files_sorted[-1])}", file=sys.stderr)
    
    print("\nЗапускаю очистку (лимит: 50 файлов)...", file=sys.stderr)
    cleanup_old_audio_files(max_files=50)
    
    mp3_files_after = glob.glob(f"{audio_dir}/*.mp3")
    print(f"\nКоличество файлов после очистки: {len(mp3_files_after)}", file=sys.stderr)

if __name__ == "__main__":
    main()














