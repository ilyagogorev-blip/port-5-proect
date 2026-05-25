# CLAUDE.md — Контент-завод (специфика проекта)

> Общие правила работы — в корневом `CLAUDE.md`. Здесь только то что специфично для контент-завода.

## Workflow IDs (актуальные)

| Воркфлоу | ID | Назначение |
|---|---|---|
| Qualifizer | `rKkJ4uRe1Jq1A47W` | Роутер задач |
| Copywriting Agent (HTML) | `qS9TfpCTIWRjhb52` | Посты в HTML через Gemini 2.5 Pro |
| Post + Image Agent | `uZeulxyswE9tOwdJ` | Пост + картинка вместе |
| News Parser | `tFT66sh8szDDXsTI` | Парсит источники каждые 12 ч |
| News Longread Writer | `tX4ug1Ziml0Owcu4` | Лонгриды → GitHub Gist |
| Image Edit Agent | `2ggvqOETRF79WSju` | NanoBanana |
| Image Gen Agent | `FatwGUsATbwCl2Lf` | Flux Pro |

**Канал публикации:** `@busybots_ai` — бот "Telegram account 2" должен быть админом.

## Supabase — критические грабли

### JSONB поля
- `tasks.source_data` и `tasks.agent_output` — **JSONB**.
- В Supabase-ноду n8n передавать **объект**: `={{ $json.source_data }}` БЕЗ `JSON.stringify(...)`.
- Если передать строку → Supabase сохранит как JSON-литерал → `valid_agent_output` constraint падает.

### Чтение JSONB
- Старые записи могут быть двойно-эскейпированными строками.
- В Code-нодах использовать `parseMaybeString()` — раскапывает до 2 уровней.

### CHECK constraint на department
```sql
ALTER TABLE tasks DROP CONSTRAINT tasks_department_check;
ALTER TABLE tasks ADD CONSTRAINT tasks_department_check
  CHECK (department IN ('copywriting', 'research', 'image_gen', 'image_edit', 'video_gen', 'post_with_image'));
```
При добавлении нового department — не забыть обновить.

## Routing (Qualifizer)

| Department | Куда роутится |
|---|---|
| `copywriting` | Copywriting Agent |
| `post_with_image` | Post + Image Agent |
| `image_gen` | Image Gen Agent |
| `image_edit` | Image Edit Agent |
| `research` | disabled |
| `video_gen` | disabled (зарезервирован под будущий Reels Maker) |

## Callback actions (inline-кнопки)

| Action | Что делает |
|---|---|
| `i:<task_id>` | Интересно → запуск Post+Image |
| `n:<task_id>` | Не интересно → удалить task |
| `pa:<task_id>` | Post Approved |
| `pr:<task_id>` | Регенерация только поста (`regen_mode='post_only'`) |
| `pf:<task_id>` | Feedback по посту (TODO) |
| `ia:<task_id>` | Image Approved |
| `im:<task_id>` | Регенерация только картинки (`regen_mode='image_only'`) |
| `if:<task_id>` | Feedback по картинке (TODO) |

**Combined publish:** оба флага (`post_approved` + `image_approved`) → `Publish to Channel` (sendPhoto с caption).

## Credentials (фиксированные ID)

| Credential | ID |
|---|---|
| Supabase account | `SuGxNLDX6DJVlYFk` |
| завод (OpenRouter) | `91TFF1bwMcnFTSML` |
| fal zavod | `Llh0AIIFyEhGQfFh` (формат: `Key <api_key>`, НЕ Bearer) |
| serper zavod | `4SHrZmoKJSHxa77m` |
| Groq API | `80oJnLwqYbKaAs1v` (Bearer) |
| Telegram account 2 | `zsy546BYqKnFttqg` |
| Аиртэйбл | `3WdCH95ATIl64ms3` |
| ScrapingBee | `7leuwTuJeija7FHs` |

**Airtable base id:** `app537M89rSzkIpIN`

## Текущие задачи в работе

> Источник правды: память + чат-история. Здесь — только долгоиграющие маркеры.

- **Стиль постов** — пользователю не нравится текущий тон Write Post. Переработать systemMessage с учётом `voice_profile.md`.
- **News Parser** — публикация финальных постов в Telegram-канал на стадии доработки.

## Чек-лист после правок воркфлоу

1. `n8n_validate_workflow` обязательно.
2. Если меняли Supabase-логику — проверить что JSONB передаётся объектом.
3. Обновить таблицу "Исправленные баги" в `README.md`.
4. Если добавили новый department — обновить CHECK constraint в Supabase + enum в Output Parser Qualifizer.
