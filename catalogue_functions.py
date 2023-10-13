import re
from product_details import get_product_page_links, parse_product_page

shop_url = 'https://www.anvibodycare.com/shop'


def send_product_info(product_data):
    product_name = product_data.get('product name', 'N/A')
    description = product_data.get('description', 'N/A')
    message = f"{product_name}\n\n"
    if description:
        message += f"Опис: {description}\n\n"
    try:
        prices = product_data.get('price', ['N/A'])[1:]

        min_price = min(int(price[2]) for price in prices)
        max_price = max(int(price[2]) for price in prices)

        message += f"Ціна: {min_price} - {max_price}₴\n"

    except ValueError:
        prices = product_data.get('price', ['N/A'])[0]
        message += f"Ціна: {prices}\n"

    return message


def get_image_for_product(product_url):
    product_data = parse_product_page(product_url)
    image_url = product_data.get('images', [])

    return image_url


def build_product_info(product_data):

    product_name = product_data['product name']

    if len(product_data['price']) == 1:
        product_price = int(re.sub(r'[^0-9]', '', product_data['price'][0]))
    else:
        product_price = sorted(product_data['price'][1:], key=lambda x: x[2])

    product_packaging_options = product_data['packaging options']
    product_weight_options = product_data['weight options']

    product_info = {
        'product name': product_name,
        'product price': product_price,
        'packaging options': product_packaging_options,
        'weight options': product_weight_options
    }

    return product_info
