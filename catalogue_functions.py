from telebot import types
from product_details import get_product_page_links, parse_product_page

shop_url = 'https://www.anvibodycare.com/shop'


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


def send_product_info(product_index):
    product_data = parse_product_page(get_product_page_links(shop_url)[product_index])
    product_name = product_data.get('product name', 'N/A')
    description = product_data.get('description', 'N/A')
    price = product_data.get('prices', ['N/A'])[0]

    message = f"{product_name}\n\n"
    message += f"Опис: {description}\n\n"
    message += f"Ціна: {price}\n"

    return message


def get_image_for_product(product_index):
    product_data = parse_product_page(get_product_page_links(shop_url)[product_index])
    image_url = product_data.get('images', [])

    return image_url


def add_to_cart_button(product_index):
    add_to_cart_button = types.InlineKeyboardButton(
        text="🛒 Купити",
        callback_data=f"add_to_cart_{product_index}"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(add_to_cart_button)

    return markup
