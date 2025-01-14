# Структура базы данных

## Таблицы

### 1. users
- **user_id** (PK): ID пользователя.
- **username**: никнейм в Telegram.
- **join_date**: дата первого появления в чате.
- **status**: активный, забанен и т.д.

### 2. messages
- **message_id** (PK): ID сообщения.
- **user_id** (FK -> users.user_id): кто отправил.
- **chat_id**: идентификатор чата (если бот обслуживает несколько чатов).
- **content**: полный текст сообщения (или кодированная версия).
- **created_at**: метка времени.

### 3. reflections
- **reflection_id** (PK): ID записи рефлексии.
- **date**: дата (день, когда рефлексия состоялась).
- **content**: сводка итогов (чему научился бот, ошибки и т.д.).
- **collective_dialog**: хранение диалога с ботом-«коллективным разумом» (либо отдельная таблица).

### 4. channels_data
- **channel_name**: “Дочка”, “Ковенант”, “Новости”.
- **post_date**: когда был сделан пост.
- **content**: что опубликовали.
- **type**: “утренние праздники”, “новостные итоги”, “тема месяца” и т.д.

### 5. media_content
- **content_id** (PK): ID контента.
- **source_link**: ссылка на YouTube, статью и т.д.
- **summary**: краткое описание (о чём видео/статья).
- **extracted_text**: субтитры или полный текст (могут быть сжаты по Huffman).
- **created_at**: когда добавили.

### 6. compression_dict (при Huffman-подходе)
- **word**: оригинальное слово.
- **code**: код, присвоенный слову.
- **frequency**: частота появления.

## Дополнительно
- Таблицы для периодических итогов (месяц, 3 месяца, 6 месяцев и т.д.) можно делать либо отдельными таблицами, либо хранить в одной, указывая тип периода (e.g. “monthly_stats”, “quarterly_stats”).
- При желании можно объединить таблицы “messages” и “media_content” (если “media_content” — всего лишь “messages” со ссылками), но сейчас логически разделяем.

---
