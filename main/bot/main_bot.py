from telebot.async_telebot import AsyncTeleBot
from django.conf import settings

bot = AsyncTeleBot(settings.TG_API_KEY, parse_mode='HTML')


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.reply_to(message, "!!!!")
