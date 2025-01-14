import os
import psycopg2
from datetime import datetime, timedelta, timezone
from telebot import TeleBot
from dotenv import load_dotenv


load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_week_start(date=None):
    if date is None:
        date = datetime.now()
    return (date - timedelta(days=date.weekday())).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

def save_message(bot: TeleBot, chat_id, user_id, message):
    conn = get_db_connection()
    cur = conn.cursor()
    user_info = bot.get_chat_member(chat_id, user_id)
    full_name = f"{user_info.user.first_name} {user_info.user.last_name or ''}".strip()
    username = f"@{user_info.user.username}" if user_info.user.username else "unknown_user"
    timestamp = datetime.now().strftime('%Y-%m-%d|%H:%M')

    if message.reply_to_message:
        replied_user_info = bot.get_chat_member(chat_id, message.reply_to_message.from_user.id)
        replied_full_name = f"{replied_user_info.user.first_name} {replied_user_info.user.last_name or ''}".strip()
        interaction_type = f"responds user {replied_full_name}"
    else:
        interaction_type = "message"

    formatted_text = f"{full_name}: {message.text}"

    # Включаем chat_id в запрос
    cur.execute("""
        INSERT INTO messages (timestamp, username, interaction_type, full_name, message_text, user_id, chat_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (timestamp, username, interaction_type, full_name, formatted_text, user_id, chat_id))

    conn.commit()
    cur.close()
    conn.close()


def get_full_context(limit=1500):
    query = """
    SELECT timestamp, username, content
    FROM messages
    ORDER BY timestamp DESC
    LIMIT ?
    """
    conn = sqlite3.connect("kraken.db")
    cursor = conn.cursor()
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    conn.close()

    # Возвращаем сообщения в обратном порядке для хронологии
    return results[::-1]


def save_participants_count(chat_id, participants_count):
    # Получаем количество участников чата через API TeleBot


    conn = get_db_connection()
    cur = conn.cursor()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Вставляем количество участников в базу данных
    cur.execute("""
        INSERT INTO participants_statistics (chat_id, participants_count, timestamp)
        VALUES (%s, %s, %s)
    """, (chat_id, participants_count, timestamp))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Сохранено количество участников для чата {chat_id}: {participants_count}")


def get_message_statistics(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    current_week_start = get_week_start()
    previous_week_start = get_week_start(current_week_start - timedelta(days=7))

    # Запрос на текущую неделю
    cur.execute("""
        SELECT COUNT(*), COUNT(DISTINCT user_id)
        FROM messages
        WHERE chat_id = %s AND timestamp >= %s AND timestamp < %s
    """, (chat_id, current_week_start, current_week_start + timedelta(weeks=1)))
    current_message_count, current_unique_users = cur.fetchone() or (0, 0)

    # Запрос на предыдущую неделю
    cur.execute("""
        SELECT COUNT(*), COUNT(DISTINCT user_id)
        FROM messages
        WHERE chat_id = %s AND timestamp >= %s AND timestamp < %s
    """, (chat_id, previous_week_start, current_week_start))
    previous_message_count, previous_unique_users = cur.fetchone() or (0, 0)

    # Закрытие соединения
    cur.close()
    conn.close()

    return {
        "current_message_count": current_message_count,
        "current_unique_users": current_unique_users,
        "previous_message_count": previous_message_count,
        "previous_unique_users": previous_unique_users,
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


def get_meme_statistics(chat_id):
    return {
        "current_total_memes_sent": 100,
        "current_memes_published": 80,
        "current_memes_deleted": 20,
        "previous_total_memes_sent": 120,
        "previous_memes_published": 100,
        "previous_memes_deleted": 30,
    }


def get_weekly_messages(chat_id):
    """Получает сообщения за текущую неделю."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем начало текущей недели
    week_start = get_week_start()

    # Извлекаем данные за текущую неделю
    cur.execute("""
        SELECT timestamp, username, interaction_type, full_name, message_text, user_id
        FROM messages
        WHERE chat_id = %s AND timestamp >= %s
    """, (chat_id, week_start))
    weekly_messages = cur.fetchall()

    cur.close()
    conn.close()

    return weekly_messages
