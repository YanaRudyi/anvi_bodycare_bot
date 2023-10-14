from telebot import types

from bot_cfg import bot
from catalogue_functions import send_product_info, get_image_for_product, build_product_info
from product_details import parse_product_page

product_identifier_map = {}


def create_product_buttons(products):
    product_identifier_map.update({product.__hash__(): product for product in products})
    product_buttons = []

    for product in products:
        product_buttons.append(
            types.InlineKeyboardButton(
                text=product.text,
                callback_data=f"product_{product.__hash__()}"
            )
        )

    return product_buttons


@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def provide_product_details(call):
    product_hash = int(call.data.split("_")[1])
    product = product_identifier_map.get(product_hash)
    product_data = parse_product_page(product.url)
    product_info_message = send_product_info(product_data)

    buy_button = types.InlineKeyboardButton(
        text="🛒 Купити",
        callback_data=f"buy_{product_hash}" if not isinstance(build_product_info(product_data)['product price'], int)
        else f"buy2_{product_hash}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(buy_button)

    image_url = get_image_for_product(product.url)
    bot.send_photo(call.message.chat.id, photo=image_url)
    bot.send_message(call.message.chat.id, product_info_message, parse_mode='HTML', reply_markup=markup)
