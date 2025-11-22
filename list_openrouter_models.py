# -*- coding: utf-8 -*-
"""Список доступных моделей OpenRouter"""
import sys
import requests
import json

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_models():
    """Получает список моделей из OpenRouter API"""
    try:
        response = requests.get('https://openrouter.ai/api/v1/models', timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"Ошибка при получении списка моделей: {e}", file=sys.stderr)
        return []

def format_price(pricing):
    """Форматирует цену для отображения"""
    if not pricing:
        return "N/A"
    
    prompt = pricing.get('prompt', '0')
    completion = pricing.get('completion', '0')
    
    if prompt == '0' and completion == '0':
        return "Бесплатно"
    
    return f"${prompt}/1M prompt, ${completion}/1M completion"

def main():
    print("=" * 80)
    print("📋 СПИСОК ДОСТУПНЫХ МОДЕЛЕЙ OPENROUTER")
    print("=" * 80)
    print("\nЗагружаю список моделей...\n")
    
    models = get_models()
    
    if not models:
        print("❌ Не удалось загрузить список моделей", file=sys.stderr)
        return
    
    print(f"Всего моделей: {len(models)}\n")
    
    # Разделяем на категории
    free_models = []
    paid_models = []
    popular_models = []
    
    popular_names = ['gpt-4', 'claude', 'gemini', 'llama', 'mistral', 'grok']
    
    for model in models:
        model_id = model.get('id', '')
        if ':free' in model_id:
            free_models.append(model)
        else:
            paid_models.append(model)
            # Проверяем популярные модели
            if any(name in model_id.lower() for name in popular_names):
                popular_models.append(model)
    
    # Бесплатные модели
    print("=" * 80)
    print(f"🆓 БЕСПЛАТНЫЕ МОДЕЛИ ({len(free_models)})")
    print("=" * 80)
    
    # Группируем по провайдерам
    by_provider = {}
    for model in free_models[:30]:  # Показываем первые 30
        model_id = model.get('id', '')
        provider = model_id.split('/')[0] if '/' in model_id else 'other'
        if provider not in by_provider:
            by_provider[provider] = []
        by_provider[provider].append(model)
    
    for provider in sorted(by_provider.keys()):
        print(f"\n📦 {provider.upper()}:")
        for model in by_provider[provider][:5]:  # По 5 от каждого провайдера
            model_id = model.get('id', '')
            name = model.get('name', model_id)
            print(f"   • {model_id}")
            print(f"     {name}")
    
    if len(free_models) > 30:
        print(f"\n   ... и еще {len(free_models) - 30} бесплатных моделей")
    
    # Популярные платные модели
    print("\n" + "=" * 80)
    print(f"⭐ ПОПУЛЯРНЫЕ ПЛАТНЫЕ МОДЕЛИ")
    print("=" * 80)
    
    # Сортируем по популярности (по id)
    popular_models_sorted = sorted(popular_models, key=lambda x: x.get('id', ''))[:20]
    
    for model in popular_models_sorted:
        model_id = model.get('id', '')
        name = model.get('name', model_id)
        pricing = model.get('pricing', {})
        price_str = format_price(pricing)
        
        print(f"\n   • {model_id}")
        print(f"     {name}")
        print(f"     💰 {price_str}")
    
    # Рекомендации
    print("\n" + "=" * 80)
    print("💡 РЕКОМЕНДАЦИИ ДЛЯ TELEGRAM БОТА")
    print("=" * 80)
    print("""
Бесплатные (для тестирования):
  • google/gemini-2.0-flash-exp:free - быстрая и бесплатная
  • meta-llama/llama-3.2-3b-instruct:free - легкая модель
  • x-ai/grok-4.1-fast:free - быстрая модель от xAI

Дешевые платные (отличное качество за небольшую цену):
  • openai/gpt-4o-mini - ~$0.15/1M токенов (текущая модель)
  • anthropic/claude-3-haiku - ~$0.25/1M токенов
  • google/gemini-pro-1.5 - хорошее качество

Премиум (максимальное качество):
  • openai/gpt-4o - ~$2.50/1M токенов
  • anthropic/claude-3.5-sonnet - ~$3/1M токенов
  • anthropic/claude-3-opus - ~$15/1M токенов (самая мощная)
    """)
    
    print("\n" + "=" * 80)
    print("📚 Полный список: https://openrouter.ai/models")
    print("=" * 80)

if __name__ == "__main__":
    main()
