# 🏭 Контент-завод

Статус: ✅ Все воркфлоу активны

Система из 7 взаимосвязанных воркфлоу для автоматического создания контента: Qualifizer принимает запросы через Telegram и роутит задачи между агентами.

---

## Воркфлоу системы

| Воркфлоу | ID | Назначение | Статус |
|---|---|---|---|
| Qualifizer | `rKkJ4uRe1Jq1A47W` | Роутер: принимает задачи из Telegram, создаёт tasks в Supabase, запускает нужный агент | ✅ |
| Copywriting Agent (HTML) | `qS9TfpCTIWRjhb52` | Пишет посты для Telegram в HTML-формате через Gemini 2.5 Pro | ✅ |
| Post + Image Agent | `uZeulxyswE9tOwdJ` | Пишет пост + генерирует картинку и отправляет оба в Telegram | ✅ NEW |
| News Parser | `tFT66sh8szDDXsTI` | Парсит новости из источников через ScrapingBee, сохраняет в Airtable | ✅ |
| News Longread Writer | `tX4ug1Ziml0Owcu4` | Пишет развёрнутые статьи на основе новостей, публикует в GitHub Gist | ✅ |
| Image Edit Agent | `2ggvqOETRF79WSju` | Редактирует изображения через NanoBanana API | ✅ |
| Image Gen Agent | `FatwGUsATbwCl2Lf` | Генерирует изображения через Flux Pro (fal.ai) | ✅ |

---

## Departments (routing в Qualifizer)

| Department | Агент |
|---|---|
| `copywriting` | Copywriting Agent |
| `post_with_image` | Post + Image Agent |
| `image_gen` | Image Gen Agent |
| `image_edit` | Image Edit Agent |
| `research` | (disabled) |
| `video_gen` | (disabled) |

---

## News Parser — автоматический сбор новостей с кнопками-фильтрами

Каждые 12 часов (Schedule Trigger) парсит источники из Airtable (RSS + Telegram-каналы), фильтрует уникальные статьи, через Gemini выбирает 5-7 топовых, создаёт задачу `post_with_image` со статусом `awaiting_review` для каждой и отправляет в Telegram **по одному сообщению с inline-кнопками**:

- 🔥 **Интересно** (`callback_data: i:<task_id>`) — статус задачи `created`, запускается Post + Image Agent
- 🚫 **Не интересно** (`callback_data: n:<task_id>`) — задача удаляется

**Источники в Airtable (`app537M89rSzkIpIN`):**
- Таблица `Источники` — поля: `RSS_Feed_URL`, `type` (rss/telegram), `name`
- Таблица `Обработанные` — URL уже виденных статей (для дедупликации)

**Парсинг по типам:**
- `rss` → нода `RSS Read` (читает feed XML)
- `telegram` → нода `Fetch Telegram Channel` (HTTP GET к `t.me/s/channel`) → `Parse Telegram Posts` (regex по HTML)

**Score & Format Digest** теперь возвращает JSON `{"items":[{"title","source","why","link"}]}`, который парсится и создаёт N задач + N сообщений с кнопками.

---

## Workflow одобрения и публикации в канал

Канал публикации: `@busybots_ai`. Бот **"Telegram account 2"** должен быть админом канала с правом Post messages.

После того как Post + Image Agent отправил пост и картинку пользователю, под каждым сообщением показываются inline-кнопки:

**Под постом:**
- ✅ Approved (`pa:<task_id>`) → отмечает `source_data.post_approved=true`
- 🔄 Миша по новой (`pr:<task_id>`) → `source_data.regen_mode='post_only'`, перезапускает Post+Image Agent, который сгенерирует только **новый пост** (картинку оставит ту же)
- ✍️ Бля ну ты че (`pf:<task_id>`) → ⚠️ feedback в разработке

**Под картинкой:**
- ✅ Approved (`ia:<task_id>`) → отмечает `source_data.image_approved=true`
- 🎲 Ещё (`im:<task_id>`) → `source_data.regen_mode='image_only'`, перезапускает Post+Image Agent → только **новая картинка** (пост остаётся)
- ✍️ Бля ну ты че (`if:<task_id>`) → ⚠️ feedback в разработке

**Логика combined publish:**
1. Пользователь жмёт Approved на пост ИЛИ картинку
2. `Set Approval Flag` Code обновляет `source_data.post_approved` или `image_approved`
3. `Save Approval State` пишет в Supabase
4. `Both Approved?` IF проверяет оба флага
5. Если **оба true** → `Publish to Channel` (Telegram sendPhoto с caption=post_text)
6. Если только один → бот пишет "Жду одобрения второго"

**Структура `agent_output` задачи (после Post + Image Agent):**
```json
{
  "versions": [
    {
      "version": 1,
      "post_text": "...",
      "image_url": "https://fal.ai/...",
      "image_prompt": "...",
      "created_at": "2026-05-11T..."
    }
  ],
  "current_version": 1
}
```

---

## Обработка callback_query в Qualifizer

`Telegram Trigger` (updates=`*`) ловит и сообщения, и callback_query от кнопок.

Поток:
```
Telegram Trigger
    → Is Callback? (IF: $json.callback_query.data notEmpty)
        TRUE → Parse Callback (Code: action + task_id)
             → Load Callback Task (Supabase: id=task_id)
             → Route Callback (Switch)
                 case 0 (i, pr, im) → Set Regen Mode (Code) → Update Task to Created → Execute Post + Image (CB)
                                       Set Regen Mode читает action и пишет в source_data.regen_mode:
                                         'i'  → null (full)
                                         'pr' → 'post_only', сброс post_approved
                                         'im' → 'image_only', сброс image_approved
                 case 1 (n)         → Delete Task
                 case 2 (pa)        → Set Approval Flag (Code, parseMaybeString) → Save → Both Approved? → Publish / Wait
                 case 3 (ia)        → то же что pa
                 case 4 (pf, if)    → Send Feedback Prompt
        FALSE → существующий поток обработки сообщений
```

---

## Post + Image Agent — актуальная информация

Запускается когда пользователь хочет пост + картинку в одном запросе.

**Пример запроса:**
```
хочу пост про Tesla Cybertruck и картинку к нему
```

**Поток (15 нод, с раздельной регенерацией):**
```
Trigger → Load Task (Supabase)
    → Prepare Context
    → Search Web (Serper — 5 актуальных результатов Google)
    → Write Post (OpenRouter/Gemini 2.5 Flash)
         Промпт: текущая дата + результаты поиска + запрос пользователя
         Возвращает JSON: { post_text: "...", image_prompt: "..." }
    → Parse Post + Image Prompt (Code — robust парсер, ловит любой регистр ключей: post_text/posttext/postText)
    → Generate Image (fal.ai flux-pro/v1.1-ultra — async queue)
    → Wait 40s
    → Get Image Result (fal.ai — response_url из очереди)
    → Prepare Update Data (Code) ⭐ NEW
         Читает task.source_data.regen_mode
         Если 'image_only' → берёт post_text из versions[-1] (старый)
         Если 'post_only'  → берёт image_url из versions[-1] (старый)
         Иначе → использует свежие данные
         Создаёт новую версию в agent_output.versions[]
    → Should Send Post? (IF) ⭐ NEW — пропускает Send Post при image_only
        TRUE → Send Post (Telegram, с inline-кнопками pa/pr/pf)
        FALSE → Should Send Image?
    → Should Send Image? (IF) ⭐ NEW — пропускает Send Image при post_only
        TRUE → Send Image (Telegram sendPhoto, с кнопками ia/im/if)
        FALSE → Update Task
    → Update Task (Supabase, agent_output = объект с versions[])
```

**Логика раздельной регенерации:**
- При `regen_mode = null` (initial) — генерирует и отправляет всё
- При `regen_mode = 'post_only'` — генерирует и отправляет только пост, картинка из старой версии переносится в новую
- При `regen_mode = 'image_only'` — отправляет только картинку, пост из старой версии переносится

**ВАЖНО — Supabase JSONB обработка:**
- `source_data` и `agent_output` нужно передавать в Supabase ноду как **объекты**, НЕ как `JSON.stringify(...)` — иначе сохранится как строка → `valid_agent_output` constraint упадёт
- При чтении из БД (Code-ноды) используй `parseMaybeString()` — старые записи могли быть сохранены как строки/двойно-строки

**Ключевые особенности:**
- AI сам генерирует `image_prompt` релевантный теме поста (не пользователю)
- Поиск Serper даёт LLM актуальные данные перед написанием
- Текущая дата инжектируется автоматически через `$now.toFormat('dd.MM.yyyy')`
- `Get Image Result` использует `response_url` из ответа fal.ai (не хардкоженный URL)

---

## Copywriting Agent — актуальная информация

Агент теперь автоматически получает текущую дату в каждом запросе:
```
Сегодня: 10.05.2026. Используй search для проверки актуальности информации по теме.

[запрос пользователя]
```

Это заставляет агента искать актуальную информацию через Serper вместо использования устаревших данных обучения.

**Robustness:** Structured Output Parser удалён. Validate Output использует 4-уровневый парсер (direct parse → escape newlines → regex extraction → use raw text as-is).

---

## Зависимости системы

Все воркфлоу используют **Supabase** как общую БД.

### Таблицы в Supabase
- `tasks` — очередь задач (создаёт Qualifizer, читают агенты)
- `sent_messages` — история отправленных сообщений

### Credentials в n8n

| Credential | ID | Используется в |
|---|---|---|
| Supabase account | `SuGxNLDX6DJVlYFk` | Все воркфлоу |
| завод (OpenRouter API) | `91TFF1bwMcnFTSML` | Image Gen, Image Edit, Post+Image, Copywriting, News Parser (Score & Format Digest) |
| fal zavod (Header Auth) | `Llh0AIIFyEhGQfFh` | Image Gen, Image Edit, Post+Image — формат: `Key <api_key>` |
| serper zavod (Header Auth) | `4SHrZmoKJSHxa77m` | Copywriting Agent, Post+Image Agent (Search Web) |
| Groq API (Header Auth) | `80oJnLwqYbKaAs1v` | Qualifizer Transcribe Audio (Whisper) — формат: `Bearer <key>` |
| Telegram account 2 | `zsy546BYqKnFttqg` | Image Gen, Image Edit, Post+Image, News Parser (Send Digest Item, Publish to Channel) |
| Аиртэйбл (Personal Access Token) | `3WdCH95ATIl64ms3` | News Parser, Longread Writer — scopes: `data.records:read/write`, `schema.bases:read` |
| ScrapingBee | `7leuwTuJeija7FHs` | News Parser (только для articles, Telegram через HTTP Request) |
| GitHub API | — | Longread Writer |

### Требуемые Railway env vars
Нет специфических для контент-завода — используют credentials напрямую.

---

## Исправленные баги

| Воркфлоу | Баг | Решение |
|---|---|---|
| Qualifizer | 7 Telegram-нод с невалидной операцией | Добавлены `resource: "message"`, `operation: "sendMessage"` |
| Qualifizer | IF "Validate AI Output": notEmpty без singleValue | Добавлен `singleValue: true` |
| Qualifizer | Execute-ноды ссылались на старые ID воркфлоу | Обновлены на актуальные ID |
| Qualifizer | Output Parser не содержал `post_with_image` в enum | Добавлен в schema: `"post_with_image"` |
| Qualifizer | Execute Post+Image: mappingMode passthrough, нет options | Исправлен через `updateNode` |
| Qualifizer | Send Confirmation: Unknown error | Известная нестабильность Telegram-ноды, не критично |
| Copywriting Agent | Serper Search не был подключён к AI Agent | Добавлена связь `ai_tool` |
| Copywriting Agent | Structured Output Parser отклонял ответы AI с tool calls | Парсер удалён, Validate Output сам извлекает JSON |
| Copywriting Agent | Update Code падал при ошибке агента | Добавлена проверка `!validateOutput.updated_agent_output` |
| Image Gen Agent | 3 Code-ноды возвращали объект вместо массива | Обёрнуты в `return [{ json: {...} }]` |
| Image Gen Agent | fal.ai credential: неверный формат Authorization | Исправлен на `Key <api_key>` вместо `Bearer` |
| Post+Image Agent | Get Image Result: URL с `/v1.1-ultra/requests/` → 405 | Заменён на `$('Generate Image').first().json.response_url` |
| Post+Image Agent | Send Image: `$json.output.images[0].url` → undefined | Заменён на `$('Get Image Result').first().json.images[0].url` |
| Post+Image Agent | Пост с устаревшей инфой, нерелевантная картинка | Добавлен Serper search + AI генерирует image_prompt из JSON |
| Post+Image Agent | Update Task падал на `valid_agent_output` constraint | Структура `agent_output` приведена к `{versions:[{version,post_text,image_url,image_prompt,created_at}], current_version}` |
| Qualifizer | Transcribe Audio: OpenRouter не поддерживает Whisper → 400 JSON error | Заменён LangChain OpenAI ноду на HTTP Request к Groq API (`whisper-large-v3-turbo`), credential "Groq API" |
| Qualifizer | Telegram отдаёт `.oga` файл, Groq требует `.ogg` | Добавлена Code-нода `Rename Voice File` перед Transcribe Audio |
| Qualifizer | Execute Post + Image терял workflowId после updateNode | Восстанавливать `__rl: true`, mode, value, cachedResultName/Url через updateNode |
| Qualifizer | Update Task to Created падал с `uuid: "undefined"` | Использовать `$('Parse Callback').first().json.task_id` вместо `$json.task_id` после Load Callback Task |
| News Parser | RSS feeds (TechCrunch, VentureBeat, MIT) возвращали 403 | Заменены на доступные источники: HackerNews, Reddit ML/Artificial, The Verge AI, LastWeekInAI |
| News Parser | Route by Type IF: ВСЕ источники попадали в False branch | Заменён IF на Switch с поиском значения "rss"/"telegram" среди ВСЕХ полей объекта (Airtable single select edge case) |
| News Parser | If date filter 24h резал всё (RSS статьи старше) | Заменён на простой `notEmpty` check (дедупликация через Обработанные таблицу) |
| News Parser | Filter Unique Articles падал на error объектах от RSS Read | Добавлен фильтр `if (j.error && j.message) continue` |
| Supabase | Airtable credential 403 Forbidden — база удалена | Новый Personal Access Token + перепривязка base ID на `app537M89rSzkIpIN` |
| Supabase | `tasks_department_check` не включал `post_with_image` | ALTER TABLE: добавлен в CHECK constraint |
| Post+Image Agent | Parse Post + Image Prompt: AI возвращал `posttext`/`imageprompt` (без underscore) → post_text = весь JSON | Robust парсер с `normalizeKeys()`: ловит posttext, post_text, postText, post-text — все варианты |
| Post+Image Agent | Раздельная регенерация (pr/im) не работала — regen_mode всегда читался как null | Source_data хранился в БД как **двойно-эскейпированная строка** (`"\"{...}\""`). Code-ноды передавали `JSON.stringify(obj)` → Supabase сохранял как JSON-литерал. Фикс: передавать **объект** напрямую (`={{ $json.source_data }}` без stringify) |
| Post+Image Agent | `valid_agent_output` constraint падал на новых записях | Та же причина — `agent_output` сохранялся строкой. Теперь передаётся объект. `parseMaybeString()` в Code-нодах раскапывает старые записи |
| Qualifizer | Set Regen Mode / Set Approval Flag читали source_data как объект, но он мог быть строкой | Добавлена `parseMaybeString()` функция, которая парсит до 2 уровней JSON-вложенности |
| News Parser | ScrapingBee community нода не установлена | Установлена через n8n Settings → Community Nodes |
| News Parser | Ссылался на старый ID Longread Writer | Обновлён на `tX4ug1Ziml0Owcu4` |
| Все воркфлоу | Telegram-ноды с невалидными операциями | Добавлены resource + operation |

---

## Порядок запуска (если с нуля)

1. Создать проект Supabase → таблицы `tasks` и `sent_messages`
2. Добавить в Supabase CHECK constraint для поля `department`:
   ```sql
   ALTER TABLE tasks DROP CONSTRAINT tasks_department_check;
   ALTER TABLE tasks ADD CONSTRAINT tasks_department_check 
     CHECK (department IN ('copywriting', 'research', 'image_gen', 'image_edit', 'video_gen', 'post_with_image'));
   ```
3. Подключить Supabase credential в n8n
4. Установить ScrapingBee community node: Settings → Community Nodes → `n8n-nodes-scrapingbee`
5. Добавить все credentials (OpenRouter, fal.ai — формат `Key <api_key>`, Serper, Airtable, GitHub, ScrapingBee)
6. Активировать агентов: Copywriting, Post+Image, Image Gen, Image Edit, News Parser, News Longread Writer
7. Активировать Qualifizer последним (он роутер и требует чтобы агенты были активны)
