# Lead Gen — Channel Discovery + Lead Scout

Автоматическая воронка холодной лидогенерации для BusyBots. Два n8n-воркфлоу связаны через общую таблицу `leads` в Supabase: Discovery её наполняет, Scout читает и обрабатывает.

## Токены и IDs

| Что | Значение |
|-----|----------|
| Илья (chat_id) | `586613159` |
| Scout бот (token) | `8445460532:AAEGKUL9sSS1rQXLk3c7_QVkrnS3urhdQ1I` |
| Scout бот env в Railway | `SCOUT_BOT_TOKEN` |
| Serper API ключ | `69a3d49d7b7d7c5c2d141a711ff89217894758a7` |

## Supabase

- Project ref: `pxaayzwzrhjmxgmqvxtb` (общий с контент-заводом)
- URL: `https://pxaayzwzrhjmxgmqvxtb.supabase.co`
- n8n credential ID: `SuGxNLDX6DJVlYFk`

### Таблица `leads`

```sql
CREATE TABLE public.leads (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  channel_username text NOT NULL,
  channel_name text,
  niche text,
  subscribers_approx int,
  status text DEFAULT 'new' CHECK (status IN
    ('new', 'processing', 'draft_ready', 'sent', 'responded', 'no_response', 'skipped')),
  kp_draft text,
  post_sample text,
  notes text,
  created_at timestamptz DEFAULT now(),
  processed_at timestamptz,
  sent_at timestamptz
);
CREATE INDEX idx_leads_status ON public.leads (status);
```

## n8n воркфлоу

| Воркфлоу | ID | Нод | Расписание |
|----------|-----|-----|------------|
| 🕵️ Channel Discovery — BusyBots | `DF3vDQDjKCKSo6iU` | 7 | Понедельник 09:00 МСК |
| 🔍 Lead Scout — BusyBots | `CeHvsRXpo3p5F0Qw` | 8 | Каждый день 10:00 МСК |

Scout Telegram credential: `9YYklU2myZrRUzmR` (BusyBots Scout Bot).

## Архитектура

```
[Channel Discovery]                    [Lead Scout]
понедельник 09:00                      каждый день 10:00
       ↓                                       ↓
  Google → Serper                      getAll status='new' LIMIT 5
       ↓                                       ↓
  Парсер t.me ссылок                   Скачать t.me/s/{username}
       ↓                                       ↓
  INSERT в leads                       Claude haiku-4-5 пишет КП
   status='new'                                ↓
       ↓                               UPDATE status='draft_ready'
   ┌───────────┐                        + kp_draft + processed_at
   │ Supabase  │ ←─────────────────────────────┘
   │  leads    │
   └───────────┘
                                       Уведомление в Scout-бота
                                       (текст КП готовый к копированию)
```

Воркфлоу независимы — связка только через статусы в БД. Можно вручную добавлять лиды в `leads` (Scout их подхватит), можно отключать Discovery (Scout продолжит работать на накопленных).

## Channel Discovery — флоу

1. **Каждый понедельник 09:00** (Schedule, cron `0 9 * * 1`)
2. **Взять существующие лиды** (Supabase getAll) — для дедупликации
3. **Список ниш** (Code, runOnceForAllItems) — 6 ниш с keyword + existingUsernames в каждом item:
   - психолог коуч → психология/коучинг
   - нутрициолог здоровье → нутрициология/здоровье
   - юрист онлайн → юристы/право
   - стоматолог клиника → стоматология/медицина
   - строительство ремонт → строительство/ремонт
   - бизнес эксперт курсы → онлайн-образование
4. **Поиск Google (Serper)** (HTTP POST `https://google.serper.dev/search`) — 6 параллельных запросов, по одному на нишу. Body JSON: `q="{keyword} telegram канал t.me"`, `num=30`, `gl=ru`, `hl=ru`
5. **Парсить каналы** (Code, runOnceForAllItems) — извлекает t.me юзернеймы regex'ом из `data.organic[].link`, фильтрует служебные (joinchat, share, addstickers...), дедуплицирует через `existingUsernames`, лимит 15 каналов на нишу
6. **Сохранить лиды** (Supabase create, continueOnFail) — INSERT в leads со status='new'
7. **Итог в Telegram** (HTTP POST, executeOnce: true) — одно сообщение "Разведка завершена. Добавлено новых лидов: N"

## Lead Scout — флоу

1. **Каждый день 10:00** (Schedule, cron `0 10 * * *`)
2. **Взять новые лиды** (Supabase getAll, filter status=new, limit 5)
3. **Скачать канал** (HTTP GET `t.me/s/{channel_username}`) — публичный preview, без авторизации
4. **Вытащить посты** (Code, runOnceForEachItem) — regex по `tgme_widget_message_text`, последние 5 постов
5. **Написать КП с Claude** (HTTP POST OpenRouter, model `anthropic/claude-haiku-4-5`) — system prompt просит 3-4 предложения персонального КП
6. **Достать КП из ответа** (Code) — парсит JSON, чистит спецсимволы Markdown через `clean()`
7. **Обновить лид в БД** (Supabase update by id) — status='draft_ready', kp_draft, processed_at=now
8. **Уведомить Илью** (HTTP POST Telegram) — КП отправляется в Scout-бот без parse_mode (чтобы спецсимволы не ломали разметку)

## Источник каналов — почему Serper

Перепробовали по убыванию приоритета:
1. **TGStat прямой HTTP** — 403 Cloudflare
2. **ScrapingBee** — бесплатный лимит закончился; платно дорого
3. **ScraperAPI** (free 1000 req/мес) — даже с `render=true premium=true ultra_premium=true` не пробивает Cloudflare TGStat (403 "current plan does not allow you to use premium proxies")
4. **Apify** — $5 кредитов навсегда, рассматривали как fallback
5. **Serper (Google)** — заработало, бесплатный план 2500 запросов/мес

Используем без оператора `site:` (бесплатный Serper отдаёт `400 "query pattern not allowed for accounts"` на site:). Просто `{keyword} telegram канал t.me` — Google и так в выдаче даёт уйму t.me ссылок.

Расход: 6 запросов × 4 недели = ~26/мес, запас огромный.

## Исправленные баги

| Баг | Симптом | Фикс |
|-----|---------|------|
| `splitInBatches` v3 | "Unknown error", itemCount=0, executionTime=1ms | Удалили ноду, соединили getAll напрямую с HTTP Request |
| Supabase update filter | "At least one select condition must be defined" | `filtersUi` не работает в update; формат `{"filters":{"conditions":[{"keyName":"id","condition":"eq","keyValue":"={{ $json.lead_id }}"}]}}` |
| Telegram "can't parse entities" | `_` в username интерпретируется как Markdown italic | Заменили Telegram-ноду на HTTP Request к `api.telegram.org/bot{TOKEN}/sendMessage` без parse_mode (плюс убирает брендинг n8n) |
| ScraperAPI 403 на TGStat | "premium pools" недоступны на бесплатном тарифе | Перешли на Serper |
| Serper 400 на site: | "query pattern not allowed for accounts" | Убрали оператор site:, ищем по обычному ключу + "t.me" в запросе |
| Парсер: "json property isn't an object" | runOnceForEachItem не отдаёт пустой массив | Переключили на runOnceForAllItems с агрегацией по индексу (search[i] ↔ niche[i]) |
| Telegram дублирует сообщение N раз | Нода получает N items на вход | `executeOnce: true` на ноде Итог в Telegram |
| Воркфлоу создан в неправильном Supabase | Создали таблицу `leads` в проекте Кента | Дропнули там, создали в проекте контент-завода (`pxaayzwzrhjmxgmqvxtb`) |

## Запуск вручную

- Discovery: открыть в n8n → Test workflow. Все 6 ниш обрабатываются параллельно, ~10-15 сек.
- Scout: тоже Test workflow. Обработает первые 5 со status='new'. Если хочешь больше — поменяй limit в ноде "Взять новые лиды".

## Что дальше

- Поля `responded` / `sent` пока не используются (Скаут только пишет драфт, рассылку Илья делает руками)
- В будущем: автоматическая отправка с задержкой 30-60 сек/сообщение + триггер по входящему ответу через Telegram webhook
- Расширить ниши когда первые 6 покажут конверсию
