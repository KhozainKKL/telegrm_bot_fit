import telebot
from telebot.async_telebot import AsyncTeleBot
from django.conf import settings

bot = AsyncTeleBot(settings.TG_API_KEY, parse_mode='HTML')
telebot.logger.setLevel(settings.LOGLEVEL)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, "Привет, друг!")


@bot.message_handler(commands=['help'])
async def send_help(message):
    await bot.reply_to(message, "Чем тебе помочь?")
