#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сброс last_update_id для тестирования"""

import os
from telegram_bot import LAST_UPDATE_ID_FILE

if os.path.exists(LAST_UPDATE_ID_FILE):
    os.remove(LAST_UPDATE_ID_FILE)
    print(f"✅ Файл {LAST_UPDATE_ID_FILE} удален")
    print("   Бот начнет обрабатывать все новые сообщения с начала")
else:
    print(f"ℹ️ Файл {LAST_UPDATE_ID_FILE} не найден (это нормально)")

