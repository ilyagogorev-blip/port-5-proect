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
| Webhook возвращал 404 на POST | У ноды Webhook не был явно задан `httpMethod` → по умолчанию слушал GET. Виджет с лендинга шлёт POST → отлуп | Прописан `parameters.httpMethod: "POST"` + передёрнут воркфлоу (deactivate/activate) для регистрации |
| Заявки от LexAI уходили **через бота Job Hunter** (`@jhunt10BOT`) — клиент путался | `Send to Admin` использовал `$env.TELEGRAM_BOT_TOKEN` (это токен Job Hunter). Создан отдельный LexAI-бот через @BotFather, добавлен `TELEGRAM_LEX_TOKEN` в Railway. URL ноды переключён на `$env.TELEGRAM_LEX_TOKEN`. Не забыть нажать `/start` боту LexAI — иначе Telegram не даст отправлять |

---

## Публичный лендинг (Netlify)

**URL:** `https://lexai-busybots.netlify.app`

Дизайн в editorial newspaper стиле (Instrument Serif + IBM Plex Sans), тёмная тема `ink`. Виджет чата в правом нижнем углу подключён к этому же webhook'у.

**Где исходник:** `sites/lexai/index.html` в корне проекта.

**Деплой через Netlify CLI:**
```powershell
cd sites/lexai
npx netlify deploy --prod --dir=.
```

Папка уже залинкована к Netlify-сайту (`.netlify/state.json` локально, проигнорирован в git).

**Webhook URL в виджете:** хардкод `https://n8n-production-0ed7.up.railway.app/webhook/lexai-chat` в JS-блоке `<script>` (поиск по `WEBHOOK_URL`).

**Структура страницы:**
- Hero — "Юридическая помощь за 30 секунд"
- §01 Почему мы — 3 карточки
- §02 Как работает — 3 шага
- §03 Пример из практики — карточка-досье
- §04 Отрасли права — 8 областей
- CTA-секция
- Footer + disclaimer

**Виджет:**
- Свернуть/развернуть кликом по шапке
- Кнопки-чипы быстрых сценариев (увольнение / залив / возврат / раздел)
- Typing-индикатор
- Error-сообщение при отвале webhook
- Disabled-состояние во время ожидания ответа

**Чтобы поменять текст / цвета / структуру:**
1. Редактируешь `sites/lexai/index.html`
2. Запускаешь `npx netlify deploy --prod --dir=.` из той же папки
3. Через 5-10 секунд новая версия в проде
4. Ctrl+F5 на странице чтобы сбросить кеш браузера

**Темы:** в `<html>` атрибут `data-theme`:
- (нет атрибута) → cream (бежевая)
- `data-theme="ink"` → тёмная (по умолчанию сейчас)
- `data-theme="noir"` → чёрно-белая

---

## Известные ограничения

- **Session key** `lexai-session` захардкожен → все пользователи делят одну память (ок для MVP, нужно исправить для продакшена)
- Бот отправляет уведомление на 586613159 при каждой новой заявке — не разделяет по клиентам
