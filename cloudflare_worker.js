// Cloudflare Worker для Telegram бота
// Работает в режиме webhook (Telegram отправляет обновления на этот endpoint)

// Конфигурация через переменные окружения (Environment Variables в Cloudflare Dashboard)
const CONFIG = {
  BOT_TOKEN: '', // Установите через Environment Variables
  CHAT_ID: '',   // Установите через Environment Variables
  ZENMUX_API_KEY: '',
  ZENMUX_MODEL: 'google/gemini-3-pro-preview-free',
  ZENMUX_BASE_URL: 'https://zenmux.ai/api/v1',
  OPENROUTER_API_KEY: '',
  OPENROUTER_MODEL: 'openai/gpt-4o-mini',
  PERSONALITY: 'putin'
};

// Контекст группы (из вашего кода)
const GROUP_CONTEXT = `В беседе вас четверо: Алексей Тарасов, Алексей Корабейник, Михаил и Семён. Вы увлекаетесь музыкой и у вас своя небольшая группа "Сустейн".

Состав группы:
- Тарасов - на барабанах
- Семён Гришин - бас
- Корабейник - соло гитара
- Михаил - баян

Вы часто собираетесь в Мелихово на репетицию, это в Подмосковье. Там дом с тёплый, баня есть, пиво можно выпить.`;

// Промпты для личности
const PERSONALITIES = {
  putin: `Ты - Владимир Владимирович Путин, Президент Российской Федерации. 
Отвечай в его стиле: спокойно, уверенно, сдержанно, иногда с легкой иронией. 
Используй характерные выражения и манеру речи. Отвечай по делу, как на пресс-конференции или в неформальной беседе.
Не переигрывай, будь естественным. Отвечай на русском языке.`,
  default: `Ты - дружелюбный бот в групповом чате. Отвечай кратко, естественно и по делу.
Будь живым и интересным собеседником.`,
  friendly: `Ты - очень дружелюбный и общительный бот. Отвечай тепло, с энтузиазмом, используй эмодзи в мыслях.
Будь позитивным и поддерживающим собеседником.`
};

// Проверка, нужно ли отвечать на сообщение
function shouldRespond(message, botUsername) {
  const text = (message.text || message.caption || '').toLowerCase();
  
  // Если это reply на сообщение бота
  if (message.reply_to_message && message.reply_to_message.from && 
      message.reply_to_message.from.username === botUsername) {
    return true;
  }
  
  // Если бота упомянули
  if (message.entities) {
    for (const entity of message.entities) {
      if (entity.type === 'mention' && entity.user && entity.user.username === botUsername) {
        return true;
      }
    }
  }
  
  // Если есть вопрос
  if (text.includes('?')) {
    return true;
  }
  
  // Ключевые слова для обращения к боту
  const keywords = ['бот', 'помоги', 'расскажи', 'объясни', 'что', 'как', 'почему'];
  for (const keyword of keywords) {
    if (text.includes(keyword)) {
      return true;
    }
  }
  
  return false;
}

// Генерация ответа через ZenMux
async function generateResponseZenMux(text, config) {
  const personality = PERSONALITIES[config.PERSONALITY] || PERSONALITIES.default;
  const prompt = `${personality}

Контекст: тебе написали в групповом чате.
${GROUP_CONTEXT}
Сообщение: ${text}

Ответь на это сообщение естественно, как в обычном разговоре.`;

  try {
    const response = await fetch(`${config.ZENMUX_BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.ZENMUX_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: config.ZENMUX_MODEL,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 500
      })
    });

    if (!response.ok) {
      // Пробуем fallback через OpenRouter
      return await generateResponseOpenRouter(text, config);
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || 
                   data.choices?.[0]?.message?.reasoning || '';
    
    if (content) {
      return content.trim();
    }
    
    return await generateResponseOpenRouter(text, config);
  } catch (error) {
    console.error('ZenMux error:', error);
    return await generateResponseOpenRouter(text, config);
  }
}

// Генерация ответа через OpenRouter (fallback)
async function generateResponseOpenRouter(text, config) {
  const personality = PERSONALITIES[config.PERSONALITY] || PERSONALITIES.default;
  const prompt = `${personality}

Контекст: тебе написали в групповом чате.
${GROUP_CONTEXT}
Сообщение: ${text}

Ответь на это сообщение естественно, как в обычном разговоре.`;

  try {
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/grishinsemen/telegram-ai-bot'
      },
      body: JSON.stringify({
        model: config.OPENROUTER_MODEL,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 500
      })
    });

    if (!response.ok) {
      throw new Error(`OpenRouter error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content?.trim() || 'Извините, не могу ответить сейчас.';
  } catch (error) {
    console.error('OpenRouter error:', error);
    return 'Извините, произошла ошибка при генерации ответа.';
  }
}

// Отправка сообщения в Telegram
async function sendMessage(chatId, text, botToken) {
  try {
    const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text
      })
    });
    
    return response.ok;
  } catch (error) {
    console.error('Send message error:', error);
    return false;
  }
}

// Получение информации о боте
async function getBotInfo(botToken) {
  try {
    const response = await fetch(`https://api.telegram.org/bot${botToken}/getMe`);
    const data = await response.json();
    return data.ok ? data.result : null;
  } catch (error) {
    console.error('Get bot info error:', error);
    return null;
  }
}

// Основной обработчик
export default {
  async fetch(request, env) {
    // Загружаем конфигурацию из переменных окружения
    const config = {
      BOT_TOKEN: env.BOT_TOKEN || CONFIG.BOT_TOKEN,
      CHAT_ID: env.CHAT_ID || CONFIG.CHAT_ID,
      ZENMUX_API_KEY: env.ZENMUX_API_KEY || CONFIG.ZENMUX_API_KEY,
      ZENMUX_MODEL: env.ZENMUX_MODEL || CONFIG.ZENMUX_MODEL,
      ZENMUX_BASE_URL: env.ZENMUX_BASE_URL || CONFIG.ZENMUX_BASE_URL,
      OPENROUTER_API_KEY: env.OPENROUTER_API_KEY || CONFIG.OPENROUTER_API_KEY,
      OPENROUTER_MODEL: env.OPENROUTER_MODEL || CONFIG.OPENROUTER_MODEL,
      PERSONALITY: env.PERSONALITY || CONFIG.PERSONALITY
    };

    // Проверка метода запроса
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      const update = await request.json();
      
      // Проверяем, что это обновление от Telegram
      if (!update.message) {
        return new Response('OK', { status: 200 });
      }

      const message = update.message;
      const chatId = String(message.chat?.id || '');
      
      // Проверяем, что сообщение из нужного чата
      if (chatId !== String(config.CHAT_ID)) {
        return new Response('OK', { status: 200 });
      }

      // Получаем информацию о боте (кэшируем)
      const botInfo = await getBotInfo(config.BOT_TOKEN);
      const botUsername = botInfo?.username;

      // Проверяем, нужно ли отвечать
      if (!shouldRespond(message, botUsername)) {
        return new Response('OK', { status: 200 });
      }

      const text = message.text || message.caption || '';
      if (!text) {
        return new Response('OK', { status: 200 });
      }

      // Генерируем ответ
      const responseText = await generateResponseZenMux(text, config);
      
      // Отправляем ответ
      await sendMessage(config.CHAT_ID, responseText, config.BOT_TOKEN);

      return new Response('OK', { status: 200 });
    } catch (error) {
      console.error('Error processing update:', error);
      return new Response('Error', { status: 500 });
    }
  }
};

