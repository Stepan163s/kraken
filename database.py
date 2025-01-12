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
    cur.execute("""
        INSERT INTO messages (timestamp, username, interaction_type, full_name, message_text)
        VALUES (%s, %s, %s, %s, %s)
    """, (timestamp, username, interaction_type, full_name, formatted_text))

    conn.commit()
    cur.close()
    conn.close()
