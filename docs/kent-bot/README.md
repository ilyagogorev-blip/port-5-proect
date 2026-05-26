# Kent Menu Bot — документация

Два Telegram бота для заказа еды. Антон готовит для Ильи и Сергея.

## Токены и IDs

| Что | Значение |
|-----|----------|
| Общий бот (token) | `8365868759:AAF-SVVgRdDJ_3H12-u0astFfwwF8dyvha4` |
| Админ бот (token) | `8808304607:AAHtXPuwjoIlSWnyiWS_raosAdkgRn4UmQc` |
| Илья | `586613159` |
| Антон (Кент, admin) | `1767504481` |
| Сергей | `765419439` |

## Supabase

- Project ref: `bytxbgnunrtltzgoljsy`
- URL: `https://bytxbgnunrtltzgoljsy.supabase.co`
- n8n credential ID: `eZBWpw00EQqNqAyn`

### Таблицы

- `menu_items` — блюда (category: first/second/dessert/drink, photo_file_id, is_available)
- `daily_choices` — выборы на каждый день (UNIQUE date+user+category)
- `battles` — КНБ сражения (user1_id, user2_id, user1_choice, user2_choice, winner_id, status, category, date)
- `user_sessions` — состояния бота (telegram_user_id, state, current_category, current_item_index)

## n8n воркфлоу

| Воркфлоу | ID | Нод |
|----------|-----|-----|
| Kent Menu Bot — Общий | `nopASC7cUG8MX8u5` | 39 |
| Kent Menu Bot — Админ | `wMYjj8RxkRoGn4AA` | 37 |

Telegram credentials: `ZwCZnd4aRhIpT3Nt` (kent-main-bot), `juCv460cGa4H4r7f` (kent-admin-bot)

## Флоу общего бота

1. `/start`, `/menu`, кнопка `📋 Меню` → приветствие + persistent reply keyboard с категориями
2. Категория (текстовая кнопка) → листаем блюда с фото, инлайн кнопки: Хочу / Некст / Хз
3. `Хочу` → сохранить выбор, показать что выбрали другие
4. Если у двух разные выборы → `По рукам` / `Ебашимся`
5. `По рукам` → заказ летит Антону в админ бот, всем подтверждение
6. `Ебашимся` → КНБ через инлайн кнопки (🪨✂️📄), оба играют независимо
7. Победитель определён → результат обоим участникам

## Флоу админ бота (Антон)

Persistent reply keyboard: `📋 Заказ` / `🍽 Бегом жрать!` / `➕ Добавить блюдо` / `📝 Список блюд`

- `📋 Заказ` → показывает все выборы за сегодня, с разбивкой победитель/проигравший если было КНБ
- `🍽 Бегом жрать!` → рассылает всем уведомление через основной бот
- `➕ Добавить блюдо` → пошагово: название → категория (инлайн) → фото или `/skip`
- `📝 Список блюд` → список всех блюд с кнопками удаления

### Состояния сессии (добавление блюда)

- `add_name` — ждёт название
- `add_cat:НАЗВАНИЕ` — ждёт выбор категории
- `add_photo:НАЗВАНИЕ:КАТЕГОРИЯ` — ждёт фото (или `/skip`)

## Архитектурные особенности

### Persistent reply keyboard
Кнопки зафиксированы над полем ввода. Отправляют **текст**, не callback_query. Parse-нода должна явно маппить текст кнопок → action.

### Cross-bot photo file_id
`file_id` фотографии привязан к конкретному боту. При добавлении блюда через админ бота:
1. Фото загружается через основной бот Илье (586613159) → получаем file_id основного бота
2. Этот file_id сохраняется в `menu_items.photo_file_id`

Ноды: `If Has Photo` → `Register Main Photo` → `Update Photo ID`

### Supabase UPSERT по составному уникальному ключу
PostgREST UPSERT с `resolution=merge-duplicates` работает только по primary key.
Для upsert по `(date, telegram_user_id, category)` нужен параметр в URL:
```
POST /daily_choices?on_conflict=date,telegram_user_id,category
```

### n8n: массив из Supabase
HTTP Request возвращает массив `[{...}, {...}]` как отдельные items.
`$input.first().json` — один объект, НЕ массив.
Всегда читать через: `$input.all().map(i => i.json)`

## Исправленные баги

| Баг | Причина | Фикс |
|-----|---------|------|
| Категории показывают "пока ничего нет" | `Array.isArray($input.first().json)` всегда false | `$input.all().map(i => i.json)` во всех Code-нодах |
| "📋 Заказ" в админ боте ничего не делает | Reply keyboard шлёт текст, Parse Admin обрабатывал только `/заказ` | Добавлены маппинги текстовых кнопок в Parse Admin |
| "➕ Добавить блюдо" и "📝 Список блюд" не работают | Та же причина — падали в `handle_text` | Добавлены маппинги `start_add` и `list_items` |
| Антону не приходит заказ | Заказ слался через основной бот, Антон его не запускал | Отправка заказа переключена на админ бот |
| "Хочу" — ошибка 409 duplicate key | `resolution=merge-duplicates` без `on_conflict` не работает по составному уникальному ключу | Добавлен `?on_conflict=date,telegram_user_id,category` в URL |
| Фото "wrong file identifier" | `file_id` привязан к боту, admin file_id не работает в main боте | Cross-bot регистрация фото через sendPhoto в main bot |
| "📋 Заказ" показывал оба выбора без победителя | Build Order Msg не знал о результатах КНБ | Добавлен `Get Battles Today`, Build Order Msg фильтрует с пометкой победитель/проигравший |
