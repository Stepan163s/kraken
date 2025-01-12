import os
from telebot import TeleBot
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = TeleBot(BOT_TOKEN)
from telebot import TeleBot
from database import (
    get_message_statistics,
    get_meme_statistics,
    get_general_statistics,
    save_message,
)

bot = TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['stats'])
def send_statistics(message):
    chat_id = message.chat.id
    response = format_statistics(chat_id)
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    save_message(bot, chat_id, user_id, message)


def get_participants_count(chat_id):
    return bot.get_chat_member_count(chat_id)




def format_statistics(chat_id):
    message_stats = get_message_statistics(chat_id)
    meme_stats = get_meme_statistics(chat_id)
    general_stats = get_general_statistics(chat_id)
    if message_stats['current_message_count'] < 1000:
        messages_formatted = (
            f"💬 Сообщений: {message_stats['current_message_count']} "
            f"({message_stats['current_message_count'] - message_stats['previous_message_count']:+})"
        )
    else:
        messages_formatted = (
            f"💬 Сообщений: {message_stats['current_message_count'] // 1000}."
            f"{(message_stats['current_message_count'] % 1000) // 100}к "
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

    # Формирование итогового ответа
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

    return f"```\n{response}\n```"  # Форматирование в стиле Telegram


