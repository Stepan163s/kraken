import os
import openai
import psycopg2
from datetime import datetime, timedelta, timezone
from telebot import TeleBot
#from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
#load_dotenv()

# Получение токенов из переменных окружения

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("CHAT_GPT_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")




# Установка API-ключа OpenAI
openai.api_key = OPENAI_API_KEY

# Инициализация бота
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Заранее заданный промпт
STYLE_PROMPT = (
    """Искажай суть в более смешную форму. Отвечай грубо, с маленькой буквы, на все поставленные вопросы в стиле пользователей из анонимных форумах..."""
    # (Сокращенный текст промпта для примера, вставьте полный текст)
)

# Установление соединения с базой данных
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Извлекает последние сообщения из базы для формирования контекста
def get_context_from_db(limit=15, hours=24):
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

    query = """
    SELECT timestamp, username, message_text
    FROM (
        SELECT timestamp, username, message_text
        FROM messages
        WHERE timestamp >= %s
        ORDER BY timestamp DESC
        LIMIT %s
    ) AS subquery
    ORDER BY timestamp ASC
    """

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, (time_threshold, limit))
    results = cur.fetchall()
    cur.close()
    conn.close()

    # Формируем строки для контекста
    return [
        f"[{timestamp}] {username}: {message_text}"
        for timestamp, username, message_text in results
    ]


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "привет! я кракен. задай мне вопрос, начав с 'кракен,'")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: "кракен" in message.text.strip().lower() or message.text.strip().endswith("?"))
def handle_message(message):
    username = message.from_user.first_name or message.from_user.username or "Друг"
    user_question = message.text[7:].strip()

    # Извлекаем контекст из базы
    context = get_context_from_db(limit=20)

    # Формируем полный промпт
    full_prompt = f"""
    {STYLE_PROMPT}

    Контекст предыдущих сообщений:
    {'\n'.join(context)}

    Зовут его {username}. Вот его вопрос:
    {user_question}
    """

    # Запрос в OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": full_prompt},
        ],
        max_tokens=500,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    bot_reply = response['choices'][0]['message']['content'].strip()
    bot.reply_to(message, bot_reply)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
