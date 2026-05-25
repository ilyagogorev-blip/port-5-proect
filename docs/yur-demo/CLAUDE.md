# CLAUDE.md — ЮР-демо / LexAI (специфика)

> Общие правила — в корневом `CLAUDE.md`. Здесь специфика.

## Workflow
- **ID:** `lt6dhGC2YE5AH805`
- **Статус:** активен
- **Тип:** Webhook (НЕ Telegram-бот) — для веб-чата на лендинге
- **Назначение:** AI-ассистент юридического сервиса. Консультация → заявка → уведомление в Telegram админу.

## Архитектура
```
Webhook (POST /lexai-chat, $json.query.message)
  → AI Agent (LexAI) + OpenAI Chat Model + Simple Memory
      ↓ success                        ↓ error
  Has New Record? ("НОВАЯ ЗАЯВКА"?)   Respond to Webhook (ошибка)
      ✅ Send to Admin (Telegram 586613159) → Respond
      ❌ Respond to Webhook (ответ клиенту)
```

## Сценарий
1. Выслушать суть проблемы
2. Назвать применимую статью (ГК РФ, ТК РФ и т.д.)
3. Объяснить практические последствия
4. Предложить консультацию юриста
5. Собрать имя + контакт (телефон/email)
6. Сформировать заявку → уведомить админа

## Области права
Семейное, трудовые споры, недвижимость, наследство, права потребителей, долги/кредиты, административные дела.

## Credentials
- **OpenAI API** id `XYzdkSQVXxoUFMOK` — OpenRouter, модель `openai/gpt-4o-mini`
- **Telegram API** id `ASP4Wb5CBiOJBdHS` "Telegram account 2" — для уведомлений админу

## КРИТИЧНО для продакшена

### Session key захардкожен
- `lexai-session` — фиксированная строка → **все пользователи делят одну память**.
- ОК для MVP/демо, НЕЛЬЗЯ для реальных клиентов.
- **Фикс:** session_key = `${client_id}-${session_id}` из webhook body.

### Admin chat id захардкожен (586613159)
- Все заявки от ВСЕХ клиентов уходят тебе.
- **Фикс:** хранить admin chat id в Supabase, привязка к domain/client_id из webhook.

## Грабли (исправленные)
- Заявка слалась после каждого сообщения → добавлена нода `Has New Record?` (IF на "НОВАЯ ЗАЯВКА")
- Telegram-нода с невалидной операцией → добавлены `resource: "message"`, `operation: "sendMessage"`
- Webhook без onError → `onError: "continueRegularOutput"`
- AI Agent и Respond to Webhook в одном выводе → разнесены

## Чек-лист после правок
1. `n8n_validate_workflow` обязательно.
2. Если меняли промпт — проверить что AI всё ещё формирует "НОВАЯ ЗАЯВКА" в конце (иначе админ не получит).
3. Перед продажей реальному клиенту — починить session key + admin chat id (см. выше).
