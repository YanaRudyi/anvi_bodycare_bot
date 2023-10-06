from product_details import get_product_page_links, parse_product_page

shop_url = 'https://www.anvibodycare.com/shop'


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

