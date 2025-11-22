# Доступные модели OpenRouter

OpenRouter предоставляет доступ к множеству моделей через единый API. Ниже список популярных моделей.

## Бесплатные модели (Free Tier)

### Google Gemini
- `google/gemini-2.0-flash-exp:free` - Экспериментальная модель Gemini 2.0 Flash (быстрая)
- `google/gemini-flash-1.5-8b:free` - Gemini Flash 1.5 (8B параметров)
- `google/gemini-pro-1.5:free` - Gemini Pro 1.5 (более мощная)

### Meta (Llama)
- `meta-llama/llama-3.2-3b-instruct:free` - Llama 3.2 3B (легкая модель)
- `meta-llama/llama-3.1-8b-instruct:free` - Llama 3.1 8B
- `meta-llama/llama-3.1-70b-instruct:free` - Llama 3.1 70B (мощная)

### Microsoft
- `microsoft/phi-3-mini-128k-instruct:free` - Phi-3 Mini (компактная и быстрая)

### Mistral AI
- `mistralai/mistral-7b-instruct:free` - Mistral 7B Instruct

## Платные модели (требуют баланс)

### OpenAI
- `openai/gpt-4o-mini` - GPT-4o Mini (быстрая и дешевая, ~$0.15/1M токенов)
- `openai/gpt-4o` - GPT-4o (самая мощная от OpenAI, ~$2.50/1M токенов)
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo (дешевая, ~$0.50/1M токенов)

### Anthropic (Claude)
- `anthropic/claude-3-haiku` - Claude 3 Haiku (быстрая, ~$0.25/1M токенов)
- `anthropic/claude-3-sonnet` - Claude 3 Sonnet (баланс скорости/качества, ~$3/1M токенов)
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet (лучшая от Anthropic, ~$3/1M токенов)
- `anthropic/claude-3-opus` - Claude 3 Opus (самая мощная, ~$15/1M токенов)

### Google
- `google/gemini-pro-1.5` - Gemini Pro 1.5 (платная версия)
- `google/gemini-2.0-flash-exp` - Gemini 2.0 Flash Experimental

### Meta
- `meta-llama/llama-3.1-405b-instruct` - Llama 3.1 405B (очень мощная)

### Mistral AI
- `mistralai/mistral-large` - Mistral Large
- `mistralai/mixtral-8x7b-instruct` - Mixtral 8x7B

### Cohere
- `cohere/command-r-plus` - Command R+
- `cohere/command-r` - Command R

## Рекомендации для Telegram бота

### Для экономии (бесплатные):
- `google/gemini-2.0-flash-exp:free` - быстрая и бесплатная
- `meta-llama/llama-3.2-3b-instruct:free` - легкая модель

### Для качества (платные, но дешевые):
- `openai/gpt-4o-mini` - отличное качество за небольшую цену
- `anthropic/claude-3-haiku` - быстрая и качественная

### Для максимального качества:
- `openai/gpt-4o` - лучшая от OpenAI
- `anthropic/claude-3.5-sonnet` - лучшая от Anthropic

## Как изменить модель

Откройте `telegram_config.json` и измените значение `openrouter_model`:

```json
{
  "openrouter_model": "openai/gpt-4o-mini"
}
```

## Полный список моделей

Для получения актуального списка всех доступных моделей посетите:
https://openrouter.ai/models

Там вы найдете:
- Полный список моделей
- Цены на каждую модель
- Скорость работы
- Контекстное окно
- Рейтинги моделей
