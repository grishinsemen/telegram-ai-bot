# Как создать новый Voice Design голос

## Шаг 1: Создание голоса на platform.minimax.io

1. Зайдите на https://platform.minimax.io/
2. Войдите в свой аккаунт
3. Перейдите в раздел **Voice Design**
4. Нажмите **"Создать новый голос"** или **"Design Voice"**
5. Введите описание голоса на английском языке, например:
   - "Deep male voice with British accent"
   - "Warm female voice with gentle tone"
   - "Mysterious narrator with suspenseful tone"
6. Нажмите **"Создать"** или **"Generate"**

## Шаг 2: Получение Voice ID

После создания голоса:
1. Найдите созданный голос в списке
2. Скопируйте **Voice ID** (обычно это строка вида `moss_audio_xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

## Шаг 3: Активация голоса

После получения Voice ID выполните:

```bash
python update_voice_id.py <ваш_новый_voice_id>
```

Например:
```bash
python update_voice_id.py moss_audio_abc123-def4-5678-90ab-cdef12345678
```

## Шаг 4: Активация через T2A API

Голос активируется автоматически при первом использовании:

```bash
python text_to_speech.py "Тест активации голоса"
```

Или используйте скрипт активации:

```bash
python activate_voice.py <ваш_новый_voice_id>
```

## Важно!

- **Voice Design голоса временные**: они удаляются через 7 дней, если не используются
- **Активация обязательна**: используйте голос в T2A API в течение 7 дней, чтобы сделать его постоянным
- **После активации**: голос становится постоянным и не будет удален

## Проверка

После активации проверьте:

```bash
python test_voice_id.py --current
```

Если голос работает, вы увидите:
```
[OK] Voice ID 'ваш_voice_id' доступен!
```

## Использование

После активации используйте голос как обычно:

```bash
python text_to_speech.py "Ваш текст здесь"
```

Аудио будет создано с использованием вашего Voice Design голоса!
















