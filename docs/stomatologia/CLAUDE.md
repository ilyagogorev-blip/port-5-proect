# CLAUDE.md — Стоматология / Ева (специфика)

> Общие правила — в корневом `CLAUDE.md`. Здесь специфика.

## Workflow
- **ID:** `F0qz2rCeBWzwuWrE`
- **Статус:** активен
- **Тип:** Telegram-бот (14 нод, с inline-кнопками)
- **Назначение:** виртуальный администратор клиники «СтомаПро». Запись на приём, консультация, уведомление админу.

## Архитектура
```
Telegram Trigger (message + callback_query)
  → Normalize Input (маппит коды кнопок в полный текст)
  → Is Start? (/start)
      ✅ Send Welcome (5 inline-кнопок)
      ❌ Answer Callback → Restore Context → AI Agent → Format Response
         → Is New Record? ("НОВАЯ ЗАПИСЬ"?)
             ✅ Send to Client + Send to Admin
             ❌ Send Response (с динамическими кнопками)
```

## Inline-кнопки welcome-экрана
| Код | Расшифровка |
|---|---|
| `record` | Записаться на приём |
| `prices` | Стоимость услуг |
| `urgent` | Острая боль — срочно |
| `cleaning` | Чистка и профилактика |
| `freewrite` | Свой вопрос |

**Лимит Telegram:** `callback_data` ≤ 64 байта → русский текст не влезает, используем короткие коды.

## Динамические кнопки (AI генерирует)
AI всегда возвращает JSON `{"text": "...", "buttons": [[...]]}`. Format Response — 4-уровневый парсер с fallback на сырой текст.

## Услуги и цены
| Услуга | Цена |
|---|---|
| Консультация | бесплатно |
| Лечение кариеса | от 3 500 ₽ |
| Удаление зуба | от 2 500 ₽ |
| Профчистка | от 4 000 ₽ |
| Отбеливание | от 8 000 ₽ |
| Коронка | от 15 000 ₽ |
| Имплантация | от 35 000 ₽ |

Режим: Пн–Пт 9–20, Сб 10–18, Вс выходной.

## Credentials
- **OpenAI API** — OpenRouter, модель `anthropic/claude-3-5-haiku`
- **Telegram API** credential "стоматология" — в Telegram Trigger

## Railway env vars
| Переменная | Зачем |
|---|---|
| `TELEGRAM_STOM_TOKEN` | Токен бота Stom.Demo (ОТДЕЛЬНЫЙ от Job Hunter!) |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` = `false` | Разрешает `$env` в нодах |

**Грабли:** оба воркфлоу не должны использовать `TELEGRAM_BOT_TOKEN` — иначе сообщения уходят не туда.

## Admin Chat ID
- Захардкожен в `Format Response`: `const ADMIN_CHAT_ID = '586613159';`
- **TODO для продакшена:** вынести в env / в БД с привязкой к клинике (мульти-тенант).

## Адаптация под другую клинику (чек-лист)
1. `systemMessage` AI Agent — заменить «СтомаПро» на новое название
2. `systemMessage` — обновить услуги и цены
3. `Send Welcome` jsonBody — обновить кнопки welcome-экрана
4. `systemMessage` — имя бота «Ева»
5. `Format Response` — заменить `ADMIN_CHAT_ID`

## Чек-лист после правок
1. `n8n_validate_workflow` обязательно.
2. Если меняли welcome-кнопки — проверить что коды ≤ 64 байта.
3. Если меняли JSON-ответ AI — прогнать через Format Response (4 уровня парсера должны выдержать).
