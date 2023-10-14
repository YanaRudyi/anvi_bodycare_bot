import os

from telebot import TeleBot

API_TOKEN = os.environ.get('ANVI_BOT_TOKEN')
bot = TeleBot(API_TOKEN)
