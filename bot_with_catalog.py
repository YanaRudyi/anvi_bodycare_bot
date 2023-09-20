import os
from telebot import types, TeleBot
from product_details import get_product_page_links, parse_product_page

API_TOKEN = os.environ.get('ANVI_BOT_TOKEN')
bot = TeleBot(API_TOKEN)

# Define the main menu keyboard
main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
product_catalog_button = types.KeyboardButton("🛍️ Каталог продуктів")
main_menu_keyboard.row(product_catalog_button)

# Handle the "/start" command
@bot.message_handler(commands=['start'])
def send_main_menu(message):
    bot.send_message(message.chat.id, "Ласкаво просимо в Anvi! Як ми можемо допомогти вам сьогодні?",
                     reply_markup=main_menu_keyboard)

# Handle the "Каталог продуктів" button
@bot.message_handler(func=lambda message: message.text == "🛍️ Каталог продуктів")
def show_product_catalog(message):
    shop_url = 'https://www.anvibodycare.com/shop'
    product_page_links = get_product_page_links(shop_url)
    product_names = []

    for link in product_page_links:
        product_info = parse_product_page(link)
        product_names.append(product_info["product name"])

    if product_names:
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for product_name in product_names:
            reply_markup.add(types.KeyboardButton(product_name))

        bot.send_message(message.chat.id, "Оберіть продукт:", reply_markup=reply_markup)
    else:
        bot.send_message(message.chat.id, "На жаль, продукти не знайдені.")

# Start the bot
if __name__ == "__main__":
    bot.polling(none_stop=True)
