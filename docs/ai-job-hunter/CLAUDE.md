# CLAUDE.md — AI Job Hunter (специфика)

> Общие правила — в корневом `CLAUDE.md`. Здесь специфика.

## Workflow
- **ID:** `zXXOZcQ3FOydPxe9`
- **Статус:** активен
- **Триггер:** Schedule, каждые 4 часа
- **Назначение:** парсинг 9 источников фриланс-вакансий → LLM-оценка → отправка ≥7/10 в Telegram

## Источники
- Remotive (5 JSON-запросов: AI automation, n8n, AI agent, Claude/OpenAI, Make/Zapier)
- We Work Remotely (RSS)
- t.me/s/freelancehunt, python_jobs, kadroff (HTML-парсинг без токена)

## Дедупликация
- `staticData.seenUrls[]` хранит до 5000 URL.
- Сброс при ручном запуске: временно `staticData.seenUrls = [];` в начале кода парсинга.

## Credentials
- **Header Auth** (OpenRouter): `Bearer sk-or-xxx`
- Telegram отправка — HTTP Request с `$env.TELEGRAM_BOT_TOKEN`
- **Chat ID получателя:** `586613159` (захардкожен в ноде отправки)

## Railway env vars
| Переменная | Значение |
|---|---|
| `N8N_ENCRYPTION_KEY` | любые 32 символа (фиксирует ключ между перезапусками) |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | `false` |
| `TELEGRAM_BOT_TOKEN` | токен Job Hunter бота |

## Известные ограничения платформ
- HH.ru API закрыт с декабря 2025
- FL.ru, Weblancer — RSS удалены
- RemoteOK, RSSHub — блокируют IP облаков
- Upwork — требует авторизованный API
- t.me/s/ — может блокироваться Cloudflare

## Чек-лист после правок
1. `n8n_validate_workflow` обязательно.
2. Если меняли формат сообщения — проверить что нет брендинга n8n (используется HTTP Request, не Telegram-нода).
