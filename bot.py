import os
import telebot

BOT_TOKEN = os.environ.get('ANVI_BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(func=lambda message: message.text.lower() == 'ping')
def send_pong(message):
    bot.reply_to(message, "pong")


bot.infinity_polling()
