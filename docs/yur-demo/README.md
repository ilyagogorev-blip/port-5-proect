# ⚖️ ЮР_демо (LexAI)

Workflow ID: `lt6dhGC2YE5AH805` | Статус: ✅ Активен

AI-ассистент юридического сервиса LexAI. Работает через **Webhook** (веб-чат, не Telegram-бот). Принимает сообщения от клиентов, консультирует по юридическим вопросам, собирает заявку, уведомляет администратора в Telegram.

---

## Архитектура (7 нод)

```
Webhook (POST /lexai-chat)
    ↓
AI Agent (LexAI) + OpenAI Chat Model + Simple Memory
    ↓ (success)                    ↓ (error)
Send to Admin (HTTP)         Respond to Webhook (ошибка)
    ↓
Has New Record? (содержит "НОВАЯ ЗАЯВКА"?)
  ✅ ДА → Send to Admin (Telegram 586613159) → Respond to Webhook
  ❌ НЕТ → Respond to Webhook (ответ клиенту)
```

---

## Тип триггера

**Webhook** — не Telegram-бот. Принимает POST-запросы:
- URL: `https://n8n.../webhook/lexai-chat`
- Входные данные: `$json.query.message` — текст сообщения от клиента
- Ответ: текст ответа AI через `Respond to Webhook`

> Этот воркфлоу предназначен для встраивания в веб-сайт как чат-виджет.

---

## Сценарий диалога

1. Выслушать суть проблемы
2. Назвать применимую статью закона (ГК РФ, ТК РФ и т.д.)
3. Объяснить практические последствия
4. Предложить консультацию юриста LexAI
5. Собрать имя и контакт (телефон или email)
6. Сформировать заявку и уведомить администратора

---

## Области права

Семейное право, трудовые споры, недвижимость, наследство, защита прав потребителей, долги и кредиты, административные дела.

---

## Настройка

### Credentials в n8n
**OpenAI API** (`XYzdkSQVXxoUFMOK` «OpenAI account»):
```
API Key:  sk-or-xxxxxxxx  ← OpenRouter ключ
Base URL: https://openrouter.ai/api/v1
```
Модель: `openai/gpt-4o-mini` (через OpenRouter)

**Telegram API** (`ASP4Wb5CBiOJBdHS` «Telegram account 2») — для уведомлений администратору

---

## Формат заявки (уходит на 586613159)

```
НОВАЯ ЗАЯВКА ⚖️
—————————————
👤 Имя: [имя]
📞 Контакт: [телефон или email]
📋 Вопрос: [краткое описание проблемы]
—————————————
```

---

## Исправленные баги

| Баг | Решение |
|---|---|
| Заявка слалась после каждого сообщения | Добавлена нода Has New Record? (IF на «НОВАЯ ЗАЯВКА») |
| Telegram-нода с невалидной операцией | Добавлены `resource: "message"`, `operation: "sendMessage"` |
| Webhook без onError | Добавлен `onError: "continueRegularOutput"` |
| AI Agent и Respond to Webhook в одном выводе | Разнесены: success → Send to Admin → Respond, error → Respond |

---

## Известные ограничения

- **Session key** `lexai-session` захардкожен → все пользователи делят одну память (ок для MVP, нужно исправить для продакшена)
- Бот отправляет уведомление на 586613159 при каждой новой заявке — не разделяет по клиентам
