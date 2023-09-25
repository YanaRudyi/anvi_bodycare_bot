import json
from product_details import get_product_page_links, parse_product_page

shop_url = 'https://www.anvibodycare.com/shop'

product_page_links = get_product_page_links(shop_url)
product_details_list = []

for link in product_page_links:
    product_info = parse_product_page(link)
    product_details_list.append(product_info)

output_file = 'product_details.json'
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(product_details_list, json_file, ensure_ascii=False, indent=4)

print(f"Data saved to {output_file}")
