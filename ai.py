import os
import openai
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

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "привет! я кракен. задай мне вопрос, начав с 'кракен,'")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: message.text.lower().startswith("кракен"))
def handle_message(message):
    # Извлечение имени пользователя
    username = message.from_user.first_name or message.from_user.username or "Друг"
    
    # Извлечение текста вопроса
    user_question = message.text[7:].strip()  # Текст после "кракен,"

    # Создание полного промпта с учетом имени пользователя
    full_prompt = f"{STYLE_PROMPT}\n\nЗовут его {username}. Вот его вопрос:\n{user_question}"

    # Запрос к OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Используем актуальную модель
        messages=[
            {"role": "user", "content": full_prompt},
        ],
        max_tokens=500,      # Максимальное количество токенов в ответе
        temperature=0.7,     # Температура генерации (от 0 до 1)
        top_p=1,             # Параметр nucleus sampling
        frequency_penalty=0, # Штраф за частоту
        presence_penalty=0,  # Штраф за присутствие
    )

    # Получение ответа от модели
    bot_reply = response.choices[0].message['content'].strip()

    # Отправка ответа пользователю
    bot.reply_to(message, bot_reply)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
