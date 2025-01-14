Ниже приведён пример файла entities.md, в котором перечислены все основные переменные, константы и функции из текущего кода. При необходимости дополняйте или уточняйте описания.

# Entities (сущности проекта)

В данном документе собраны основные переменные, функции и объекты, используемые в коде.  

## 1. Переменные окружения (Environment Variables)

- **BOT_TOKEN**  
  Токен Telegram-бота, загружается через `os.getenv("BOT_TOKEN")`.
- **CHAT_GPT_TOKEN**  
  Ключ OpenAI API, загружается через `os.getenv("CHAT_GPT_TOKEN")`.
- **DB_HOST**  
  Хост PostgreSQL, загружается через `os.getenv("DB_HOST")`.
- **DB_NAME**  
  Название базы данных PostgreSQL, загружается через `os.getenv("DB_NAME")`.
- **DB_USER**  
  Пользователь БД, загружается через `os.getenv("DB_USER")`.
- **DB_PASSWORD**  
  Пароль для доступа к БД, загружается через `os.getenv("DB_PASSWORD")`.
- **DB_PORT**  
  Порт подключения к БД, загружается через `os.getenv("DB_PORT")` (используется в `database.py`).
- **CHAT_ID**  
  Идентификатор чата (канала/группы), на котором запускается бот, загружается через `os.getenv("CHAT_ID")`.

## 2. ai.py

**Переменные**  
- `TELEGRAM_BOT_TOKEN`  
  Получен из `os.getenv("BOT_TOKEN")`.
- `OPENAI_API_KEY`  
  Получен из `os.getenv("CHAT_GPT_TOKEN")`.
- `DB_HOST, DB_NAME, DB_USER, DB_PASSWORD`  
  Параметры для подключения к БД, также загружаются через `os.getenv(...)`.
- `bot` (объект `TeleBot`)  
  Инициализирован с помощью `TELEGRAM_BOT_TOKEN`.
- `STYLE_PROMPT` (строка)  
  Пример заготовленного промпта для ChatGPT в грубом стиле.

**Функции**  
- `get_db_connection()`  
  Возвращает соединение `psycopg2.connect(...)` к PostgreSQL на основе переменных окружения.
- `get_context_from_db(limit=15, hours=24)`  
  Извлекает последние сообщения (за заданное количество часов/штук) из таблицы `messages`, возвращает список строк формата `"[timestamp] username: message_text"`.
- Обработчики для бота (`@bot.message_handler`):
  - `send_welcome(message)`  
    Отправляет приветствие при команде `/start`.
  - `handle_message(message)`  
    Обрабатывает текстовые сообщения, если они содержат ключевое слово “кракен” или заканчиваются вопросительным знаком. Формирует `full_prompt` и делает запрос к OpenAI API.

## 3. database.py

**Переменные**  
- `DB_CONFIG` (словарь)  
  Содержит основные настройки подключения к PostgreSQL: `dbname`, `user`, `password`, `host`, `port`.

**Функции**  
- `get_db_connection()`  
  Создаёт и возвращает соединение `psycopg2.connect(**DB_CONFIG)`.
- `get_week_start(date=None)`  
  Возвращает дату начала недели (понедельник 00:00:00) для текущей или указанной даты.
- `save_message(bot, chat_id, user_id, message)`  
  Сохраняет сообщение в таблицу `messages` (timestamp, username, interaction_type, full_name, text и т.д.).
- `get_full_context(limit=1500)`  
  (Судя по коду, не дописано или неактуально) Предположительно возвращает последние сообщения из `kraken.db` (SQLite), хотя остальной код работает с PostgreSQL.  
- `save_participants_count(chat_id, participants_count)`  
  Сохраняет в таблицу `participants_statistics` текущее количество участников чата.
- `get_message_statistics(chat_id)`  
  Сравнивает количество сообщений и уникальных пользователей за текущую и предыдущую недели.
- `get_general_statistics(chat_id)`  
  Извлекает “участников” (participants) и “истории” (stories) из таблицы `general_statistics` за текущую и предыдущую недели.
- `get_meme_statistics(chat_id)`  
  Возвращает статистику по заявкам на мемы, числу одобренных/отклонённых (пока заглушка).
- `get_weekly_messages(chat_id)`  
  Извлекает сообщения из таблицы `messages` за текущую неделю (с начала недели).

## 4. handlers.py

**Переменные**  
- `BOT_TOKEN`  
  Снова загружается через `os.getenv('BOT_TOKEN')`.  
- `bot` (объект `TeleBot`)  
  Инициализируется вторично (однако реальный проект стоит аккуратно использовать один экземпляр).

**Функции**  
- `handle_top_command(message)`  
  При команде `/top` выгружает сообщения за текущую неделю (`get_weekly_messages`) и отправляет их в виде файла.
- `send_statistics(message)`  
  При команде `/stats` вызывает `format_statistics(chat_id)` и отправляет результат.
- `handle_message(message)`  
  Обработчик для всех входящих сообщений (сохранение сообщения в БД через `save_message`).
- `get_participants_count(chat_id)`  
  Вызывает `bot.get_chat_member_count(chat_id)`, чтобы узнать количество участников.
- `format_statistics(chat_id)`  
  Формирует итоговую строку статистики (обсуждения, мемы, общая статистика и т.д.).

## 5. main.py

**Переменные**  
- `CHAT_ID`  
  Читается из `.env`, указывает на ID чата, для которого собирается статистика.
- `bot`  
  Импортируется из `handlers.py`.
- `scheduler` (объект `BackgroundScheduler`)  
  Из библиотеки `apscheduler.schedulers.background`.

**Функции**  
- `update_statistics()`  
  Вызывает `get_participants_count(CHAT_ID)` и `save_participants_count(CHAT_ID, participants_count)`, чтобы раз в минуту сохранять статистику по участникам.

**Принцип работы**  
- Запуск планировщика `scheduler.add_job(..., 'interval', minutes=1)`.
- Запуск бесконечного поллинга бота `bot.infinity_polling(...)`.

## 6. prompts.py

**Функции/Константы**  
- `get_current_date()`  
  Возвращает текущую дату в формате `"%d %B %Y"`.
- `HOLIDAY_PROMPT` (строка)  
  Пронт “Какой сегодня праздник?” с добавленной текущей датой.
- `STYLE_PROMPT` (строка)  
  Основной “характер”/“манера” бота: грубость, мат, ссылки на политику, паранойю и т.д.

---

## Дополнительно

1. **Структура проекта**  
   - `knowledge/`, `reflexion/`, `sleep/`, `speak/`, `task/` — директории с файлами, не показанными целиком. Предположительно содержат логику публикаций, модулей для генерации контента, “ночной” рефлексии и т.д.  
   - `schema.sql` — SQL-схема (не показана). Скорее всего хранит описание таблиц `messages`, `participants_statistics`, `general_statistics` и других сущностей.

2. **Дубликаты переменных**  
   - В `ai.py` и `handlers.py` одинаково загружается `BOT_TOKEN`. При рефакторинге стоит свести это к одному месту (например, вынести в конфигурационный модуль).

3. **Безопасность**  
   - Все токены и пароли берутся из `.env` (через `os.getenv`), не хранятся открыто в репозитории.

4. **Важные замечания**  
   - Некоторые функции (например, `get_full_context`) используют SQLite, но основные функции — PostgreSQL. Возможно, потребуется унификация (или это переходный период разработки).
   - Модель в запросе к OpenAI указана как `"gpt-4o-mini"` (в `ai.py`). При необходимости меняйте на актуальную модель (`gpt-3.5-turbo`, `gpt-4` и т.п.).
