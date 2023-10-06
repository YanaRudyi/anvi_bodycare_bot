import os

from telebot import types, TeleBot

from catalogue_functions import send_product_info, get_image_for_product
from product_details import get_product_page_names

from writing_questions_to_spreadsheet import write_to_spreadsheet

shop_url = 'https://www.anvibodycare.com/shop'
API_TOKEN = os.environ.get('ANVI_BOT_TOKEN')
bot = TeleBot(API_TOKEN)

main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
product_catalog_button = types.KeyboardButton("🛍️ Товари")
about_us_button = types.KeyboardButton("🏢 Про нас")
contact_us_button = types.KeyboardButton("📞 Наші контакти")
search_button = types.KeyboardButton("🔍 Пошук")
help_button = types.KeyboardButton("👋 Допомога")

main_menu_keyboard.row(product_catalog_button)
main_menu_keyboard.row(about_us_button)
main_menu_keyboard.row(contact_us_button)
main_menu_keyboard.row(search_button)
main_menu_keyboard.row(help_button)


@bot.message_handler(commands=['start'])
def send_main_menu(message):
    bot.send_message(message.chat.id, "Вітаємо в Anvi! Як ми можемо допомогти вам сьогодні?",
                     reply_markup=main_menu_keyboard)


help_requested = {}


@bot.message_handler(func=lambda message: message.text == "👋 Допомога")
def provide_help(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Будь ласка, залиште ваші дані і повідомлення і ми вам зателефонуємо")
    help_requested[user_id] = True


@bot.message_handler(func=lambda message: help_requested.get(message.chat.id, False) and message.text != "🛍️ Product Catalog")
def handle_message(message):
    if message.chat.id in help_requested:
        write_to_spreadsheet(message)
        bot.send_message(message.chat.id, "Дякуємо! Ми скоро з Вами зв'яжемось.")
        del help_requested[message.chat.id]


@bot.message_handler(func=lambda message: message.text == "🔍 Пошук")
def provide_search(message):
    bot.send_message(message.chat.id, "Введіть параметри запиту:")


@bot.message_handler(func=lambda message: message.text == "📞 Наші контакти")
def provide_contact_info(message):
    bot.send_message(message.chat.id, "Ви можете зв'язатись з нами через anvibodycare@gmail.com.")


@bot.message_handler(func=lambda message: message.text == "🏢 Про нас")
def provide_about_us_info(message):
    bot.send_message(message.chat.id, "Ми Anvi. Турбота про ваше тіло – наша головна мета!")


@bot.message_handler(func=lambda message: message.text == "🛍️ Товари")
def show_product_catalog(message):
    product_buttons = create_product_buttons()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*product_buttons)
    bot.send_message(message.chat.id, "Оберіть товар:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def provide_product_details(call):
    product_index = int(call.data.split("_")[1])
    product_info_message = send_product_info(product_index)
    add_to_cart_markup = add_to_cart_button(product_index)

    image_url = get_image_for_product(product_index)
    bot.send_photo(call.message.chat.id, photo=image_url)
    bot.send_message(call.message.chat.id, product_info_message, parse_mode='HTML',
                     reply_markup=add_to_cart_markup)


def create_product_buttons():
    product_buttons = []
    names = get_product_page_names(shop_url)

    for index, product_name in enumerate(names):
        product_buttons.append(
            types.InlineKeyboardButton(
                text=product_name,
                callback_data=f"product_{index}"
            )
        )

    return product_buttons


def add_to_cart_button(product_index):
    add_to_cart_button = types.InlineKeyboardButton(
        text="🛒 Купити",
        callback_data=f"add_to_cart_{product_index}"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(add_to_cart_button)

    return markup


bot.polling()
