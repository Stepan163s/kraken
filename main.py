from handlers import bot
from apscheduler.schedulers.background import BackgroundScheduler
from database import save_participants_count

import os
from dotenv import load_dotenv
load_dotenv()
CHAT_ID = os.getenv('CHAT_ID')

def update_statistics():
    save_participants_count(CHAT_ID)

scheduler = BackgroundScheduler()
scheduler.add_job(update_statistics, 'interval', minutes=30)
scheduler.start()

if __name__ == "__main__":
    bot.infinity_polling(timeout=30, long_polling_timeout=25)
