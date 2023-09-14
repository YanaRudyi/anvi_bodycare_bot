import os

from telebot import types, TeleBot

API_TOKEN = os.environ.get('ANVI_BOT_TOKEN')
bot = TeleBot(API_TOKEN)

main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
product_catalog_button = types.KeyboardButton("🛍️ Каталог продуктів")
about_us_button = types.KeyboardButton("🏢 Про нас")
contact_us_button = types.KeyboardButton("📞 Контакти")
search_button = types.KeyboardButton("🔍 Пошук")
help_button = types.KeyboardButton("👋 Допомога")

main_menu_keyboard.row(product_catalog_button)
main_menu_keyboard.row(about_us_button)
main_menu_keyboard.row(contact_us_button)
main_menu_keyboard.row(search_button)
main_menu_keyboard.row(help_button)


@bot.message_handler(commands=['start'])
def send_main_menu(message):
    bot.send_message(message.chat.id, "Ласкаво просимо в Anvi! Як ми можемо допомогти вам сьогодні?",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda message: message.text == "👋 Допомога")
def provide_help(message):
    bot.send_message(message.chat.id, "Будь ласка, залишіть ваші дані і ми вам зателефонуємо")


@bot.message_handler(func=lambda message: message.text == "🔍 Пошук")
def provide_search(message):
    bot.send_message(message.chat.id, "Введіть параметри запиту:")


@bot.message_handler(func=lambda message: message.text == "📞 Контакти")
def provide_contact_info(message):
    bot.send_message(message.chat.id, "Ви можеш зв'язатись з нами через anvibodycare@gmail.com.")


@bot.message_handler(func=lambda message: message.text == "🏢 Про нас")
def provide_about_us_info(message):
    bot.send_message(message.chat.id, "Ми Anvi. Забота про ваше тіло – наша головна мета!")


@bot.message_handler(func=lambda message: message.text == "🛍️ Каталог продуктів")
def provide_products(message):
    bot.send_message(message.chat.id, "Наші продукти: ")


bot.infinity_polling()
