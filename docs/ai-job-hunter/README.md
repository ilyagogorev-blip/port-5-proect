# 🤖 AI Job Hunter

Workflow ID: `zXXOZcQ3FOydPxe9` | Статус: ✅ Активен

Автоматический агент, который каждые 4 часа сканирует международные площадки и Telegram-каналы в поиске фриланс-проектов по AI-автоматизации и отправляет релевантные находки в Telegram.

---

## Как работает

```
⏰ Каждые 4 часа
    ↓
📋 9 источников (Remotive × 5, WeWorkRemotely, Telegram × 3)
    ↓
📡 Загрузка данных (RSS / JSON API / HTML-парсинг)
    ↓
🔄 Парсинг + дедупликация (помнит до 5000 просмотренных вакансий)
    ↓
🤖 AI-оценка каждой вакансии (OpenRouter / GPT-4o-mini)
    ↓
✅ Фильтр: только оценка ≥ 7/10
    ↓
📬 Отправка в Telegram (прямой HTTP-запрос, без брендинга n8n)
```

---

## Источники

| Источник | Тип | Поисковые запросы |
|---|---|---|
| Remotive.com | JSON API | AI automation, n8n, AI agent/chatbot/LLM, Claude/OpenAI, Make/Zapier |
| We Work Remotely | RSS | Programming jobs |
| t.me/s/freelancehunt | HTML | Парсинг постов без токена |
| t.me/s/python_jobs | HTML | Парсинг постов без токена |
| t.me/s/kadroff | HTML | Парсинг постов без токена |

---

## Формат сообщения в Telegram

```
🌍 Mid/Senior AI Engineer

🏷 AI, automation, ML
⭐ 9/10
💡 Проект включает разработку AI/ML моделей и агентных систем

🔗 https://remotive.com/remote-jobs/...
```

---

## Настройка

### Переменные окружения Railway
| Переменная | Значение |
|---|---|
| `N8N_ENCRYPTION_KEY` | любые 32 символа (фиксирует ключ между перезапусками) |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | `false` |
| `TELEGRAM_BOT_TOKEN` | токен Job Hunter бота от @BotFather |

### Credentials в n8n
**Header Auth** (OpenRouter):
```
Name:  Authorization
Value: Bearer sk-or-xxxxxxxxxxxxxxxx
```

### Chat ID
В ноде `📬 Отправка в Telegram` прописан напрямую: `586613159`

---

## Известные проблемы и решения

| Проблема | Причина | Решение |
|---|---|---|
| 0 вакансий при ручном запуске | Все URL уже в seenUrls | Временно добавить `staticData.seenUrls = [];` в начало кода парсинга |
| После перезапуска Railway credentials не работают | Новый ключ шифрования | Добавить `N8N_ENCRYPTION_KEY` в Railway и переоткрыть credentials в n8n UI |
| Credential «Header Auth account» не расшифровывается | Создан до установки `N8N_ENCRYPTION_KEY` | Удалить старый, создать новый с тем же OpenRouter ключом |

---

## Ограничения платформ

- **HH.ru** — API закрыт с декабря 2025
- **FL.ru, Weblancer** — RSS-ленты удалены
- **RemoteOK, RSSHub** — блокируют IP облачных серверов
- **Upwork** — RSS удалён, требует авторизованный API
- **Telegram t.me/s/** — могут блокироваться Cloudflare
