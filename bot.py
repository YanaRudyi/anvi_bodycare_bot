import os

from telebot import types, TeleBot

API_TOKEN = os.environ.get('ANVI_BOT_TOKEN')
bot = TeleBot(API_TOKEN)

main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
product_catalog_button = types.KeyboardButton("🛍️ Product Catalog")
about_us_button = types.KeyboardButton("🏢 About Us")
contact_us_button = types.KeyboardButton("📞 Contact Us")
search_button = types.KeyboardButton("🔍 Search")
help_button = types.KeyboardButton("📞 Help")

main_menu_keyboard.row(product_catalog_button)
main_menu_keyboard.row(about_us_button)
main_menu_keyboard.row(contact_us_button)
main_menu_keyboard.row(search_button)
main_menu_keyboard.row(help_button)


@bot.message_handler(commands=['start'])
def send_main_menu(message):
    bot.send_message(message.chat.id, "Welcome to AnviBodyCare! How can we assist you today?",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda message: message.text == "📞 Help")
def provide_help(message):
    bot.send_message(message.chat.id, "Будь ласка, залишіть ваші дані і ми вам зателефонуємо")


@bot.message_handler(func=lambda message: message.text == "🔍 Search")
def provide_search(message):
    bot.send_message(message.chat.id, "Введіть параметри запиту:")


@bot.message_handler(func=lambda message: message.text == "📞 Contact Us")
def provide_contact_info(message):
    bot.send_message(message.chat.id, "Ти можеш зв'язатись з нами через anvibodycare@gmail.com.")


@bot.message_handler(func=lambda message: message.text == "🏢 About Us")
def provide_about_us_info(message):
    bot.send_message(message.chat.id, "Ми Anvi. Забота про ваше тіло – наша головна мета!")


@bot.message_handler(func=lambda message: message.text == "🛍️ Product Catalog")
def provide_products(message):
    bot.send_message(message.chat.id, "Наші продукти: ")


bot.infinity_polling()
