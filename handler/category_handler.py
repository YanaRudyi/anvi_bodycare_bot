from telebot import types

from bot_cfg import bot
from handler.product_handler import create_product_buttons
from product_details import get_products

category_url_dict = {
    'тіло': 'https://anvibodycare.com/product-category/tilo/',
    'обличчя': 'https://anvibodycare.com/product-category/oblychchia/',
    'волосся': 'https://anvibodycare.com/product-category/volossia/',
}


def create_category_buttons():
    return [types.InlineKeyboardButton(
        text=category.title(),
        callback_data=f'category_{category.lower()}'
    ) for category in category_url_dict]


@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def show_products_for_category(call):
    selected_category = call.data.split("_")[1]
    products = get_products_for_category(selected_category)
    product_buttons = create_product_buttons(products)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*product_buttons)
    # Do not delete whitespaces, it needs for button width
    bot.send_message(call.message.chat.id,
                     f"Оберіть товар у категорії {selected_category}:⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
                     reply_markup=markup)


def get_products_for_category(category):
    url = category_url_dict.get(category)
    return get_products(url)
