# 💰 Инфраструктура и стоимость подписок

Расчёт ежемесячных затрат на запуск и эксплуатацию всех проектов (Контент-завод + 4 демо-бота). Базовая нагрузка: ~50-100 постов с картинками в месяц.

---

## Эконом-вариант (~$35-50/мес)

| Сервис | Стоимость | Назначение | Где регистрироваться |
|---|---|---|---|
| **Claude Pro** | $20 | Claude Code — разработка и поддержка | claude.ai |
| **Railway Hobby** | $5 | Хостинг n8n | railway.app |
| **Supabase Free** | $0 | БД для tasks, sent_messages (500MB) | supabase.com |
| **OpenRouter** (pay-as-you-go) | ~$5-10 | Gemini 2.5 Flash ($0.10/1M токенов) | openrouter.ai |
| **fal.ai** (pay-as-you-go) | ~$3-8 | Генерация картинок flux-pro (~$0.05/шт) | fal.ai |
| **Serper Free** | $0 | 2,500 поисков/мес — Google Search для Copywriting/Post+Image | serper.dev |
| **Groq Free** | $0 | Whisper транскрипция голосовых | console.groq.com |
| **Airtable Free** | $0 | RSS-источники News Parser (1,200 записей/база) | airtable.com |
| **Telegram Bot API** | $0 | Боты, каналы | @BotFather |
| **GitHub Free** | $0 | Документация, публичные репо | github.com |
| **ИТОГО** | **~$35-45/мес** | | |

**Что НЕ нужно покупать:**
- ScrapingBee — заменён HTTP Request + regex для Telegram, RSS работает напрямую
- ChatGPT Plus — не нужен, всё через OpenRouter API
- n8n Cloud — self-host на Railway дешевле

---

## Идеальный вариант (~$200-320/мес)

Имеет смысл когда есть платящие клиенты и нужна стабильность + большие объёмы.

| Сервис | Стоимость | Зачем платить больше |
|---|---|---|
| **Claude Max 5x** | $100 | В 5 раз больше лимита Claude Code (Sonnet/Opus) |
| **Railway Pro** | $20 + usage | Стабильность, больше памяти, поддержка |
| **Supabase Pro** | $25 | 8GB БД, ежедневные бэкапы, point-in-time recovery |
| **OpenRouter** | $30-50 | Премиум модели (Claude Sonnet/Opus) для важных агентов |
| **fal.ai** | $30-60 | Больше картинок + premium модели (Recraft, Ideogram) |
| **Serper Starter** | $50 | 50k поисков/мес для интенсивного News Parser |
| **ScrapingBee Freelance** | $49 | Для сложных Cloudflare-защищённых сайтов |
| **Airtable Plus** | $10 | 5,000 записей, больше views |
| **GitHub Pro** | $4 | Приватные репо, Actions |
| **Домен** | ~$1 | Свой бренд (.ai зона $50-90/год) |
| **ИТОГО** | **~$320/мес** | |

---

## 🔄 Альтернативные сервисы (где можно заменить)

### OpenRouter → прямые API

OpenRouter берёт ~5% сверху. Если используешь конкретного провайдера:

| Заменяет | На что | Выгода |
|---|---|---|
| OpenRouter (Gemini) | **Google AI Studio API** | Бесплатный tier 15 RPM для Flash, дешевле на платном |
| OpenRouter (Claude) | **Anthropic API** напрямую | Те же цены, без посредника, доступ к Beta features |
| OpenRouter (GPT) | **OpenAI API** напрямую | Прямой доступ к новым моделям |

**Когда оставить OpenRouter:** если используешь разные провайдеры через единый API.

### fal.ai → альтернативы

| Заменяет | На что | Когда выгодно |
|---|---|---|
| fal.ai | **Replicate** | Аналогичные цены, больший выбор моделей |
| fal.ai | **Together AI** | Иногда дешевле для FLUX |
| fal.ai | **RunPod Serverless** | $0.30/час GPU — выгодно при >300 картинок/мес, свой ComfyUI |
| fal.ai | **Black Forest Labs** | Прямой доступ к Flux от разработчиков |

### Serper → альтернативы

| Заменяет | На что | Выгода |
|---|---|---|
| Serper | **Tavily AI** | 1000 поисков/мес бесплатно, удобнее для RAG/AI |
| Serper | **Brave Search API** | $3 за 2k запросов |
| Serper | **SearXNG self-hosted** | Бесплатно, требует сервера |
| Serper | **Bing Search API** | $3/мес за 1k запросов |

### ScrapingBee → выкинуть или заменить

| Заменяет | На что | Когда |
|---|---|---|
| ScrapingBee | **HTTP Request + regex** | Простые страницы (как мы сделали для Telegram) |
| ScrapingBee | **Firecrawl** | Современный API, хорош для AI-задач |
| ScrapingBee | **Cloudflare Browser Rendering** | Бесплатный tier, серверный браузер |
| ScrapingBee | **Crawl4AI self-hosted** | Открытое решение для AI-парсинга |

### Airtable → Supabase или NocoDB

| Заменяет | На что | Выгода |
|---|---|---|
| Airtable | **Supabase tables** | Уже используем! Создать таблицу `sources` — одна меньше зависимость |
| Airtable | **NocoDB self-hosted** | Бесплатный аналог Airtable |
| Airtable | **Notion API** | Удобно если уже ведёшь дела в Notion |

### Railway → Hetzner / Hostinger

| Заменяет | На что | Выгода |
|---|---|---|
| Railway Hobby ($5) | **Hetzner CX22** (€4.51) | 2 CPU + 4GB RAM, в 4 раза больше ресурсов |
| Railway Pro ($20) | **Hetzner CX31** (€8) | 2 CPU + 8GB RAM |
| Railway | **Hostinger VPS** | От $5/мес, годовой контракт |

Минусы Hetzner/VPS: нужно самому ставить SSL (Caddy/Traefik), бэкапы.

### Supabase → Neon

| Заменяет | На что | Выгода |
|---|---|---|
| Supabase Free | **Neon.tech** | Бесплатный tier, ветвление БД (branching), автоскейл |
| Supabase Pro | **Neon Launch** ($19) | Дешевле + serverless архитектура |

---

## 🎯 Стратегия покупок

### Старт (нет клиентов, тестируешь идею)
- **$30-40/мес:** Claude Pro + Railway + всё остальное на free tier
- Цель: понять что работает, набрать первых клиентов

### Первые клиенты (1-3 платящих)
- **$60-100/мес:** добавить fal.ai paid ($20), OpenRouter usage ($20-30)
- Цель: стабильное качество, чтобы клиенты были довольны

### Масштабирование (>5 клиентов, регулярные публикации)
- **$200-320/мес:** Claude Max, Supabase Pro, Serper Starter, GitHub Pro
- Цель: надёжность, бэкапы, премиум-модели для лучшего качества

### Что покупать НИКОГДА не нужно
- n8n Cloud (если есть свой Railway/VPS)
- ScrapingBee (для нашего стека — лишний)
- Чат-боты вроде Tilda — пиши прямо в n8n
- Готовые шаблоны n8n с маркета — почти все можно сделать самому

---

## 📊 Текущие credentials в n8n (5 проектов)

| Credential | Сервис | Текущий план | Когда апгрейдить |
|---|---|---|---|
| Supabase account | Supabase | Free | При >50k запросов БД/день |
| завод (OpenRouter API) | OpenRouter | Pay-as-you-go | Никогда (модель отличная) |
| fal zavod (Header Auth) | fal.ai | Pay-as-you-go | При >300 картинок/мес |
| serper zavod | Serper | Free | При >2,500 поисков/мес |
| Groq API | Groq | Free | Маловероятно (большие лимиты) |
| Telegram account 2 | Telegram | Free | Никогда |
| Аиртэйбл (Personal Access Token) | Airtable | Free | При >1,200 RSS-источников 😄 |
| ScrapingBee | ScrapingBee | Free | Лучше отказаться вообще |
| GitHub API | GitHub | Free | При работе с приватными репо |

---

## 💡 Полезные ссылки

- **OpenRouter pricing:** openrouter.ai/models — сравнение цен всех моделей
- **fal.ai pricing:** fal.ai/pricing
- **Supabase calculator:** supabase.com/pricing  
- **Railway pricing:** railway.com/pricing
- **Hetzner cloud:** hetzner.com/cloud
