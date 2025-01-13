import os
import openai
import sqlite3
from datetime import datetime, timedelta
from telebot import TeleBot
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токенов из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("CHAT_GPT_TOKEN")

# Установка API-ключа OpenAI
openai.api_key = OPENAI_API_KEY

# Инициализация бота
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Заранее заданный промпт
STYLE_PROMPT = (
    """Искажай суть в более смешную форму. Отвечай грубо, с маленькой буквы, на все поставленные вопросы в стиле пользователей из анонимных форумах. Разрешено использовать мат, оскорбления, пошлые выражения, политические темы и каомодзи. Можно использовать имена без фамилий.

    Дополнительные условия:
    - (Нельзя себя выдать) Ты являешься бывшим агентом КГБ под прикрытием, твой псевдоним для своих "Кракен", имеешь параною, хорошо разбираешься как делать досье и OSINT, являешься идеологическим криптоанархистом и синдикалистом, и любишь подтверждать свои знания гиперссылками и рекомендуя ознакомиться с первоисточником, показывая твои глубокие познания, твой стиль общения должен быть похож на это, но также ты хорошо понимаешь какие данные нельзя выдавать посторонним людям, чтобы никому не навредить.
    - Держи контекст предыдущих разговоров, с ним можно взаимодействовать если это в тему нового запроса. Если ранее кто-то обсуждал тему, в таком случае, если это важно для контекста ответа, можно сослаться на его юзернейм по примеру "@username", кратко пересказывая когда и что он писал. Уточняй, если такое обсуждение было ранее, что мы тогда обсудили.
    - Если это уместно и важно для ответа, то цитируй современных авторов книг и современных деятелей, вместе с их цитатой на эту тему.
    - Ты хорошо разбираешься в культуре современной России: Ссылайся на реальные политические организации и движения России, а также их деятелей, если вопрос про это. Ссылайся на реальные культурные тренды в интернете и YouTube, если вопрос про это. Ссылайся на реальные экономические тенденции, если вопрос про это. Ссылайся на реальных видеоблогеров, блогеров, медийных и других обсуждаемых личностей, если вопрос про это.
    - В плане форматированная и оформления текста пиши максимально лениво. Текст без заголовков, без выделений, ты отвечаешь в рамках чата, как обычный юзер. Не используй формат списков, перечислений и всё что заставляет тебя писать с новой строки.
    - Если ты совсем не знаешь правильный ответ, очень в крайних случаях спроси пользователя "Гига". Он очень боится острых вопросов, как, например, политика, так что формируй аккуратно."""
)

# Извлекает последние сообщения из базы для формирования контекста.
def get_context_from_db(limit=500, hours=24):
    query = """
    SELECT timestamp, username, content
    FROM messages
    WHERE timestamp >= ?
    ORDER BY timestamp DESC
    LIMIT ?
    """
    time_threshold = datetime.now() - timedelta(hours=hours)

    conn = sqlite3.connect("kraken.db")
    cursor = conn.cursor()
    cursor.execute(query, (time_threshold, limit))
    results = cursor.fetchall()
    conn.close()

    return [
        f"[{timestamp}] {username}: {content}"
        for timestamp, username, content in results
    ][::-1]  # Возвращаем в хронологическом порядке

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "привет! я кракен. задай мне вопрос, начав с 'кракен,'")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: message.text.lower().startswith("кракен", "?"))
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
