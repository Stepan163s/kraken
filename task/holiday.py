import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from prompts import HOLIDAY_PROMPT, STYLE_PROMPT

bot = telebot.TeleBot(BOT_TOKEN)

# Получение текущей даты в формате для запроса
def get_formatted_date():
    now = datetime.now(pytz.timezone("Europe/Moscow"))
    return now.strftime("%d %B %Y")

# Формирование текста сообщения
def generate_message():
    today_date = get_formatted_date()
    message = f"{today_date}. {HOLIDAY_PROMPT}\n\n{STYLE_PROMPT}"
    return message

# Отправка сообщения в канал
def post_to_channel():
    message = generate_message()
    bot.send_message(CHANNEL_NAME, message)

# Планировщик публикаций
scheduler = BackgroundScheduler(timezone="Europe/Moscow")
scheduler.add_job(post_to_channel, 'cron', hour=7, minute=0)
scheduler.start()
