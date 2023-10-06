from product_details import get_product_page_links, parse_product_page

shop_url = 'https://www.anvibodycare.com/shop'


def send_product_info(product_index):
    product_data = parse_product_page(get_product_page_links(shop_url)[product_index])
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


def get_image_for_product(product_index):
    product_data = parse_product_page(get_product_page_links(shop_url)[product_index])
    image_url = product_data.get('images', [])

    return image_url

