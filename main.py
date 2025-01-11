import telebot
import psycopg2
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler

DB_CONFIG = {
    'dbname': 'user_data',
    'user': '',
    'password': '',
    'host': '',
    'port': 5432
}

BOT_TOKEN = ''
bot = telebot.TeleBot(BOT_TOKEN)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_week_start(date=None):
    if date is None:
        date = datetime.now()
    return (date - timedelta(days=date.weekday())).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

def save_message(chat_id, user_id, message):
    conn = get_db_connection()
    cur = conn.cursor()

    # Получение информации о текущем пользователе из Telegram
    user_info = bot.get_chat_member(chat_id, user_id)
    full_name = f"{user_info.user.first_name} {user_info.user.last_name or ''}".strip()
    username = f"@{user_info.user.username}" if user_info.user.username else "unknown_user"

    # Текущее время
    timestamp = datetime.now().strftime('%Y-%m-%d|%H:%M')

    # Определяем тип взаимодействия
    if message.reply_to_message:  # Если это ответ на сообщение
        replied_user_info = bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)
        replied_full_name = f"{replied_user_info.user.first_name} {replied_user_info.user.last_name or ''}".strip()
        interaction_type = f"responds user {replied_full_name}"
    else:  # Обычное сообщение
        interaction_type = "message"

    # Формируем текст сообщения в нужном формате
    formatted_text = f"{full_name}: {message.text}"

    # Формируем итоговый текст записи
    formatted_message = f"{timestamp}|{username}|{interaction_type}|{formatted_text}"

    # Записываем данные в базу
    cur.execute("""
        INSERT INTO messages (timestamp, username, interaction_type, full_name, message_text)
        VALUES (%s, %s, %s, %s, %s)
    """, (timestamp, username, interaction_type, full_name, formatted_text))

    conn.commit()
    cur.close()
    conn.close()

def get_participants_count(chat_id):
    try:
        return bot.get_chat_members_count(chat_id)
    except:
        return 0

def save_participants_count(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    week_start = get_week_start()
    participants_count = get_participants_count(chat_id)
    cur.execute("""
        INSERT INTO general_statistics (chat_id, week_start, participants, stories)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (chat_id, week_start) DO UPDATE
        SET participants = EXCLUDED.participants
    """, (chat_id, week_start, participants_count, 0))
    conn.commit()
    cur.close()
    conn.close()

def update_meme_statistics_weekly(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    week_start = get_week_start()
    cur.execute("""
        SELECT SUM(total_memes_sent), SUM(memes_published), SUM(memes_deleted)
        FROM user_meme_statistics
    """)
    total_memes_sent, memes_published, memes_deleted = cur.fetchone()
    cur.execute("""
        INSERT INTO meme_statistics_weekly (chat_id, week_start, total_memes_sent, memes_published, memes_deleted)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (chat_id, week_start) DO UPDATE
        SET total_memes_sent = EXCLUDED.total_memes_sent,
            memes_published = EXCLUDED.memes_published,
            memes_deleted = EXCLUDED.memes_deleted
    """, (chat_id, week_start, total_memes_sent or 0, memes_published or 0, memes_deleted or 0))
    conn.commit()
    cur.close()
    conn.close()

def get_message_statistics(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    current_week_start = get_week_start()
    previous_week_start = get_week_start(current_week_start - timedelta(days=7))
    cur.execute("""
        SELECT COUNT(*), COUNT(DISTINCT user_id)
        FROM messages
        WHERE chat_id = %s AND message_date >= %s AND message_date < %s
    """, (chat_id, current_week_start, current_week_start + timedelta(weeks=1)))
    current_message_count, current_unique_users = cur.fetchone() or (0, 0)
    cur.execute("""
        SELECT COUNT(*), COUNT(DISTINCT user_id)
        FROM messages
        WHERE chat_id = %s AND message_date >= %s AND message_date < %s
    """, (chat_id, previous_week_start, current_week_start))
    previous_message_count, previous_unique_users = cur.fetchone() or (0, 0)
    cur.close()
    conn.close()
    return {
        "current_message_count": current_message_count,
        "current_unique_users": current_unique_users,
        "previous_message_count": previous_message_count,
        "previous_unique_users": previous_unique_users,
    }

def get_meme_statistics(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    current_week_start = get_week_start()
    previous_week_start = get_week_start(current_week_start - timedelta(days=7))

    cur.execute("""
        SELECT total_memes_sent, memes_published, memes_deleted
        FROM meme_statistics_weekly
        WHERE chat_id = %s AND week_start = %s
    """, (chat_id, current_week_start))
    current_meme_stats = cur.fetchone() or (0, 0, 0)
    cur.execute("""
        SELECT total_memes_sent, memes_published, memes_deleted
        FROM meme_statistics_weekly
        WHERE chat_id = %s AND week_start = %s
    """, (chat_id, previous_week_start))
    previous_meme_stats = cur.fetchone() or (0, 0, 0)
    cur.close()
    conn.close()
    return {
        "current_total_memes_sent": current_meme_stats[0],
        "current_memes_published": current_meme_stats[1],
        "current_memes_deleted": current_meme_stats[2],
        "previous_total_memes_sent": previous_meme_stats[0],
        "previous_memes_published": previous_meme_stats[1],
        "previous_memes_deleted": previous_meme_stats[2],
    }

def get_general_statistics(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    current_week_start = get_week_start()
    previous_week_start = get_week_start(current_week_start - timedelta(days=7))
    cur.execute("""
        SELECT participants, stories
        FROM general_statistics
        WHERE chat_id = %s AND week_start = %s
    """, (chat_id, current_week_start))
    current_general_stats = cur.fetchone() or (0, 0)
    cur.execute("""
        SELECT participants, stories
        FROM general_statistics
        WHERE chat_id = %s AND week_start = %s
    """, (chat_id, previous_week_start))
    previous_general_stats = cur.fetchone() or (0, 0)
    cur.close()
    conn.close()
    return {
        "current_participants": current_general_stats[0],
        "current_stories": current_general_stats[1],
        "previous_participants": previous_general_stats[0],
        "previous_stories": previous_general_stats[1],
    }

def format_statistics(chat_id):
    message_stats = get_message_statistics(chat_id)
    meme_stats = get_meme_statistics(chat_id)
    general_stats = get_general_statistics(chat_id)

    # Форматирование статистики
    messages_formatted = (
        f"💬 Сообщений: {message_stats['current_message_count'] // 1000}.{(message_stats['current_message_count'] % 1000) // 100}к "
        f"({message_stats['current_message_count'] - message_stats['previous_message_count']:+})"
    )
    users_formatted = (
        f"👀 Участники дискуссий: {message_stats['current_unique_users']} "
        f"({message_stats['current_unique_users'] - message_stats['previous_unique_users']:+})"
    )
    memes_formatted = (
        f"📨 Заявок: {meme_stats['current_total_memes_sent']} "
        f"({meme_stats['current_total_memes_sent'] - meme_stats['previous_total_memes_sent']:+}) | "
        f"📬 Одобрено: {meme_stats['current_memes_published']} "
        f"({meme_stats['current_memes_published'] - meme_stats['previous_memes_published']:+}) | "
        f"📭 Отклонено: {meme_stats['current_memes_deleted']} "
        f"({meme_stats['current_memes_deleted'] - meme_stats['previous_memes_deleted']:+})"
    )
    participants_formatted = (
        f"🌚 Участники: {general_stats['current_participants']} "
        f"({general_stats['current_participants'] - general_stats['previous_participants']:+})"
    )
    stories_formatted = (
        f"🔖 Истории: {general_stats['current_stories']} "
        f"({general_stats['current_stories'] - general_stats['previous_stories']:+})"
    )

    # Формирование итогового ответа в цитате
    response = (
        f"Тема месяца\n"
        f"🔥 Обсуждение сервиса Яндекс Книги\n\n"
        f"Активность\n"
        f"{messages_formatted} | {users_formatted}\n\n"
        f"Мем-предложка\n"
        f"{memes_formatted}\n\n"
        f"Общая статистика\n"
        f"{participants_formatted} | {stories_formatted}"
    )

    return f"```\n{response}\n```"  # Форматирование в стиле цитаты Telegram


@bot.message_handler(commands=['sta'])
def send_statistics(message):
    chat_id = message.chat.id
    get_weekly_topic(chat_id)

@bot.message_handler(commands=['top'])
def send_statistics(message):
    chat_id = message.chat.id
    export_and_send_weekly_messages_txt(chat_id, output_file="weekly_messages.txt")

@bot.message_handler(commands=['stats'])
def send_statistics(message):
    chat_id = message.chat.id
    response = format_statistics(chat_id)
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    message_text = message.text
    save_message(chat_id, user_id, message_text)

def update_statistics():
    chat_id = CHAT_ID
    save_participants_count(chat_id)
    update_meme_statistics_weekly(chat_id)

scheduler = BackgroundScheduler()
scheduler.add_job(update_statistics, 'interval', minutes=30)
scheduler.start()



def get_weekly_messages(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Определяем начало текущей недели
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())

    # Извлекаем сообщения за последнюю неделю
    cur.execute("""
        SELECT message_text
        FROM messages
        WHERE chat_id = %s AND message_date >= %s
    """, (chat_id, week_start))
    messages = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return messages


from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(messages):
    vectorizer = TfidfVectorizer(max_features=100)
    tfidf_matrix = vectorizer.fit_transform(messages)
    feature_array = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1

    # Сортируем ключевые слова по значимости
    keywords = sorted(zip(scores, feature_array), reverse=True)[:5]
    return [word for _, word in keywords]



def get_weekly_topic(chat_id):
    messages = get_weekly_messages(chat_id)

    if not messages:
        print("Не удалось определить тему недели.")
        return

    # Ключевые слова
    keywords = extract_keywords(messages)

    # Выводим в консоль

    bot.send_message(chat_id, text = f"Тема недели: {', '.join(keywords[:3])}")

import csv

def export_and_send_weekly_messages_txt(chat_id, output_file="weekly_messages.txt"):
    conn = get_db_connection()
    cur = conn.cursor()

    # Определяем начало текущей недели
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())

    # Извлекаем сообщения за неделю
    cur.execute("""
        SELECT m.user_id, m.telegram_name, m.message_text, m.message_date
        FROM messages m
        WHERE m.chat_id = %s AND m.message_date >= %s
    """, (chat_id, week_start))
    messages = cur.fetchall()

    cur.close()
    conn.close()

    if not messages:
        bot.send_message(chat_id, "Нет сообщений за текущую неделю.")
        return

    # Создаем TXT файл
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("User ID | Telegram Name | Message Text | Timestamp\n")
        f.write("-" * 60 + "\n")  # Разделительная линия
        for user_id, telegram_name, message_text, message_date in messages:
            formatted_date = message_date.strftime('%Y-%m-%d %H:%M')  # Форматируем дату и время
            # Формируем строку данных
            f.write(f"{user_id} | {telegram_name} | {message_text} | {formatted_date}\n")

    # Отправляем TXT файл в Telegram-чат
    with open(output_file, "rb") as f:
        bot.send_document(chat_id, f)

    print(f"Сообщения успешно сохранены в файл {output_file} и отправлены в чат.")

if __name__ == "__main__":
    bot.infinity_polling(timeout=30, long_polling_timeout=25)
