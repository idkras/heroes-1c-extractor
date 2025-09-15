# Примеры использования внешнего API

В этом документе представлены примеры использования внешнего API Advising Platform для интеграции со Slack и Telegram.

## Аутентификация

Для всех запросов необходимо использовать токен доступа, который передается в заголовке `Authorization`:

```
Authorization: Bearer YOUR_API_TOKEN
```

Для Slack и Telegram используются разные токены, которые настраиваются в переменных окружения:
- `ADVISING_API_SLACK_TOKEN` - токен для Slack
- `ADVISING_API_TELEGRAM_TOKEN` - токен для Telegram

## Обновление контекста проекта из Slack

```bash
curl -X POST https://advising-platform.heroes.camp/api/v1/external/slack/action \
  -H "Authorization: Bearer YOUR_SLACK_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Slack-Request-Timestamp: $(date +%s)" \
  -H "X-Slack-Signature: SLACK_SIGNATURE" \
  -d @slack_meeting_context.json
```

## Создание задачи из Telegram

```bash
curl -X POST https://advising-platform.heroes.camp/api/v1/external/telegram/action \
  -H "Authorization: Bearer YOUR_TELEGRAM_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: TELEGRAM_SIGNATURE" \
  -d @telegram_create_task.json
```

## Создание инцидента из Telegram

```bash
curl -X POST https://advising-platform.heroes.camp/api/v1/external/telegram/action \
  -H "Authorization: Bearer YOUR_TELEGRAM_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: TELEGRAM_SIGNATURE" \
  -d @telegram_create_incident.json
```

## Получение информации о проекте

```bash
curl -X POST https://advising-platform.heroes.camp/api/v1/external/slack/action \
  -H "Authorization: Bearer YOUR_SLACK_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Slack-Request-Timestamp: $(date +%s)" \
  -H "X-Slack-Signature: SLACK_SIGNATURE" \
  -d '{
    "action": "get_project_summary",
    "project_id": "heroes.camp"
  }'
```

## Поиск по документам

```bash
curl -X POST https://advising-platform.heroes.camp/api/v1/external/telegram/action \
  -H "Authorization: Bearer YOUR_TELEGRAM_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: TELEGRAM_SIGNATURE" \
  -d '{
    "action": "search",
    "query": "проблемы с чекпоинтами",
    "project": "advising_platform",
    "document_type": "task",
    "limit": 5
  }'
```

## Интеграция со Slack-ботом

Для интеграции со Slack можно использовать Slack API и Bolt Framework:

```javascript
const { App } = require('@slack/bolt');

// Инициализация приложения Slack
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
});

// Обработка команды /advising-context
app.command('/advising-context', async ({ command, ack, say, client }) => {
  // Подтверждение получения команды
  await ack();

  // Получение текста запроса
  const text = command.text;
  const parts = text.split(' ');
  if (parts.length < 2) {
    await say('Необходимо указать проект и тип контекста. Например: `/advising-context heroes.camp meeting`');
    return;
  }

  const project = parts[0];
  const contextType = parts[1];

  // Открытие модального окна для ввода данных контекста
  try {
    await client.views.open({
      trigger_id: command.trigger_id,
      view: {
        type: 'modal',
        callback_id: 'advising_context_modal',
        title: {
          type: 'plain_text',
          text: 'Обновление контекста проекта'
        },
        blocks: [
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `Обновление контекста для проекта *${project}*`
            }
          },
          {
            type: 'input',
            block_id: 'title',
            label: {
              type: 'plain_text',
              text: 'Название'
            },
            element: {
              type: 'plain_text_input',
              action_id: 'title_input'
            }
          },
          {
            type: 'input',
            block_id: 'summary',
            label: {
              type: 'plain_text',
              text: 'Краткое описание'
            },
            element: {
              type: 'plain_text_input',
              multiline: true,
              action_id: 'summary_input'
            }
          }
          // Дополнительные поля в зависимости от типа контекста
        ],
        submit: {
          type: 'plain_text',
          text: 'Отправить'
        }
      }
    });
  } catch (error) {
    console.error(error);
    await say('Произошла ошибка при открытии формы ввода контекста');
  }
});

// Обработка отправки формы
app.view('advising_context_modal', async ({ ack, body, view, client }) => {
  // Подтверждение получения формы
  await ack();

  // Извлечение данных из формы
  const title = view.state.values.title.title_input.value;
  const summary = view.state.values.summary.summary_input.value;

  // Формирование запроса к Advising Platform API
  const requestData = {
    action: 'update_context',
    context: {
      project: 'heroes.camp', // Извлекаем из скрытого поля или контекста
      namespace: 'meetings',   // Извлекаем из типа контекста
      version: '1.0',
      data: {
        type: 'meeting',
        title: title,
        summary: summary,
        // Другие поля в зависимости от типа контекста
      }
    }
  };

  // Отправка запроса к Advising Platform API
  try {
    const response = await fetch('https://advising-platform.heroes.camp/api/v1/external/slack/action', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.ADVISING_API_SLACK_TOKEN}`,
        'Content-Type': 'application/json',
        'X-Slack-Request-Timestamp': Math.floor(Date.now() / 1000).toString(),
        'X-Slack-Signature': 'CALCULATED_SIGNATURE', // В реальном коде вычисляется на основе запроса
      },
      body: JSON.stringify(requestData),
    });

    const result = await response.json();

    // Отправка сообщения пользователю о результате
    await client.chat.postMessage({
      channel: body.user.id,
      text: result.success 
        ? `✅ Контекст успешно обновлен: ${result.message}` 
        : `❌ Ошибка при обновлении контекста: ${result.message}`
    });
  } catch (error) {
    console.error(error);
    await client.chat.postMessage({
      channel: body.user.id,
      text: '❌ Произошла ошибка при отправке данных в Advising Platform'
    });
  }
});
```

## Интеграция с Telegram-ботом

Для интеграции с Telegram можно использовать node-telegram-bot-api:

```javascript
const TelegramBot = require('node-telegram-bot-api');
const crypto = require('crypto');
const axios = require('axios');

// Создание бота
const token = process.env.TELEGRAM_BOT_TOKEN;
const bot = new TelegramBot(token, { polling: true });

// Обработка команды /task
bot.onText(/\/task (.+)/, async (msg, match) => {
  const chatId = msg.chat.id;
  const taskText = match[1];
  
  // Разбор текста задачи (например, формат: "Заголовок | Проект | Приоритет | Описание")
  const parts = taskText.split('|').map(part => part.trim());
  
  if (parts.length < 3) {
    bot.sendMessage(chatId, 'Неверный формат задачи. Используйте: `/task Заголовок | Проект | Приоритет | Описание`');
    return;
  }
  
  const title = parts[0];
  const project = parts[1];
  const priority = parts[2].toUpperCase();
  const description = parts.length > 3 ? parts[3] : '';
  
  // Формирование данных задачи
  const taskData = {
    action: 'create_task',
    task: {
      title,
      project,
      priority,
      description,
      assignee: `@${msg.from.username || 'unknown'}`
    }
  };
  
  try {
    // Вычисление подписи запроса
    const secretKey = crypto.createHash('sha256').update(token).digest();
    const data = JSON.stringify(taskData);
    const signature = crypto.createHmac('sha256', secretKey).update(data).digest('hex');
    
    // Отправка запроса к API
    const response = await axios.post('https://advising-platform.heroes.camp/api/v1/external/telegram/action', data, {
      headers: {
        'Authorization': `Bearer ${process.env.ADVISING_API_TELEGRAM_TOKEN}`,
        'Content-Type': 'application/json',
        'X-Telegram-Bot-Api-Secret-Token': signature
      }
    });
    
    const result = response.data;
    
    if (result.success) {
      bot.sendMessage(chatId, `✅ Задача успешно создана: ${result.message}\nID: ${result.task.id}`);
    } else {
      bot.sendMessage(chatId, `❌ Ошибка при создании задачи: ${result.message}`);
    }
  } catch (error) {
    console.error(error);
    bot.sendMessage(chatId, '❌ Произошла ошибка при отправке данных в Advising Platform');
  }
});

// Обработка команды /incident
bot.onText(/\/incident (.+)/, async (msg, match) => {
  // Аналогично обработке задач, но для инцидентов
  // ...
});
```

## Обработка данных на стороне Advising Platform

Примеры того, как данные, полученные через API, обрабатываются и сохраняются в системе:

1. Данные контекста сохраняются в соответствующие файлы проекта
2. Задачи добавляются в todo.md с соблюдением установленного формата
3. Инциденты регистрируются в ai.incidents.md

Это позволяет поддерживать единую систему учета и отслеживания задач и инцидентов, независимо от источника их создания.