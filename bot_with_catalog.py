import os
from telebot import types, TeleBot
from product_details import get_product_page_links, parse_product_page

shop_url = 'https://www.anvibodycare.com/shop'
API_TOKEN = os.environ.get('ANVI_BOT_TOKEN')
bot = TeleBot(API_TOKEN)


def create_product_buttons():
    product_buttons = []
    links = get_product_page_links(shop_url)

    for index, link in enumerate(links):
        product_data = parse_product_page(link)
        product_name = product_data.get('product name')
        product_buttons.append(
            types.InlineKeyboardButton(
                text=product_name,
                callback_data=f"product_{index}"
            )
        )

    return product_buttons


main_menu_keyboard = types.InlineKeyboardMarkup(row_width=1)
product_catalog_button = types.InlineKeyboardButton(
    "🛍️ Каталог продуктів", callback_data="catalog"
    )
about_us_button = types.InlineKeyboardButton(
    "🏢 Про нас", callback_data="about_us"
    )
contact_us_button = types.InlineKeyboardButton(
    "📞 Контакти", callback_data="contact_us"
    )
search_button = types.InlineKeyboardButton(
    "🔍 Пошук", callback_data="search"
    )
help_button = types.InlineKeyboardButton(
    "👋 Допомога", callback_data="help"
    )

main_menu_keyboard.add(
    product_catalog_button,
    about_us_button,
    contact_us_button,
    search_button,
    help_button
    )


@bot.message_handler(commands=['start'])
def send_main_menu(message):
    bot.send_message(message.chat.id, "Вітаємо в Anvi! Як ми можемо допомогти вам сьогодні?",
                     reply_markup=main_menu_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "help")
def provide_help(call):
    bot.send_message(call.message.chat.id, "Будь ласка, залишіть ваші дані і ми вам зателефонуємо")


@bot.callback_query_handler(func=lambda call: call.data == "search")
def provide_search(call):
    bot.send_message(call.message.chat.id, "Введіть параметри запиту:")


@bot.callback_query_handler(func=lambda call: call.data == "contact_us")
def provide_contact_info(call):
    bot.send_message(call.message.chat.id, "Ви можете зв'язатись з нами через anvibodycare@gmail.com.")


@bot.callback_query_handler(func=lambda call: call.data == "about_us")
def provide_about_us_info(call):
    bot.send_message(call.message.chat.id, "Ми Anvi. Турбота про ваше тіло – наша головна мета!")


@bot.message_handler(commands=['start'])
def send_catalog_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    catalog_button = types.InlineKeyboardButton(
        text="🛍️ Каталог продуктів",
        callback_data="catalog"
    )
    markup.add(catalog_button)
    bot.send_message(message.chat.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "catalog")
def show_product_catalog(call):
    product_buttons = create_product_buttons()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*product_buttons)
    bot.send_message(call.message.chat.id, "Оберіть продукт:", reply_markup=markup)


bot.polling()
