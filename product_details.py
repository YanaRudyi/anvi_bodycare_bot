import json
import re

import cachetools
import requests
from bs4 import BeautifulSoup


cache = cachetools.TTLCache(maxsize=1, ttl=3600)


def get_product_page_links(shop_url):
    product_page_links = {}

    response = requests.get(shop_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_links = soup.find_all('a', href=True)

        for link in product_links:
            product_page_url = link['href']
            if 'product-page' in product_page_url:
                product_page_links[product_page_url] = True

        return list(product_page_links.keys())

    return []


def parse_product_page(url):
    def extract_product_name(json_path):
        return json_path("name")

    def extract_description(json_path):
        return json_path("description")

    def extract_prices(json_path):
        product_items = json_path("productItems", [])
        formatted_prices = [item.get("formattedPrice") for
                            item in product_items]
        return formatted_prices

    def extract_weight_volume(json_path):
        options_list = json_path("options", [])
        weight_volume = []
        for option in options_list[:1]:
            if "selections" in option and isinstance(
                    option["selections"], list):
                for selection in option["selections"]:
                    if "key" in selection:
                        weight_volume.append(selection["key"])
        return weight_volume

    def extract_packaging(json_path):
        options_list = json_path("options", [])
        packaging_values = []
        if len(options_list) > 1:
            second_option = options_list[1]
            if "selections" in second_option and isinstance(
                    second_option["selections"], list):
                for selection in second_option["selections"]:
                    if "value" in selection:
                        packaging_values.append(selection["value"])
        return packaging_values

    def extract_additional_info(json_path):
        additional_info_list = json_path("additionalInfo", [])
        for info in additional_info_list:
            info.pop("id", None)
            info.pop("index", None)
        return additional_info_list

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve product page: {url}")

    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find("script", {
        "type": "application/json", "id": "wix-warmup-data"
    })

    if not script_tag:
        raise Exception('Script tag not found.')

    json_data = json.loads(script_tag.string)
    dynamic_key = next((key for key in json_data.get(
        "appsWarmupData", {}).get(
        "1380b703-ce81-ff05-f115-39571d94dfcd", {})
                        if key.startswith("productPage_UAH_")), None)

    if not dynamic_key:
        raise Exception('Dynamic key not found in JSON data.')

    json_path = json_data.get("appsWarmupData", {}).get(
        "1380b703-ce81-ff05-f115-39571d94dfcd", {}).get(
        dynamic_key, {}).get(
        "catalog").get(
        "product", {}).get

    def clean_html(raw_html):
        tag_replacements = {
            '&nbsp;': ' ',
            '<\/p>|<\/li>|<br>': '\n',
            '<li>': '\n🔹 ',
            '<strong>|<\/strong>|<p>|<ul>|<\/ul>|<u>|<\/u>': '',
        }

        for tag, replacement in tag_replacements.items():
            raw_html = re.sub(tag, replacement, raw_html)

        return raw_html.strip()

    def clean_html_entities(data):
        if isinstance(data, str):
            return clean_html(data)
        elif isinstance(data, list):
            return [clean_html_entities(item) for item in data]
        elif isinstance(data, dict):
            cleaned_dict = {}
            for key, value in data.items():
                cleaned_dict[key] = clean_html_entities(value)
            return cleaned_dict
        else:
            return data

    def get_images(json_path):
        images = json_path("media", [])
        if images:
            first_image = images[0]
            full_url = first_image.get("fullUrl")
            if full_url:
                return full_url
        return None

    product_name = extract_product_name(json_path)
    description = extract_description(json_path)
    formatted_prices = extract_prices(json_path)
    weight_volume = extract_weight_volume(json_path)
    packaging_values = extract_packaging(json_path)
    additional_info_list = extract_additional_info(json_path)
    image_urls = get_images(json_path)

    product_details = {
        "product name": clean_html_entities(product_name),
        "description": clean_html_entities(description),
        "prices": clean_html_entities(formatted_prices),
        "weight_volume": clean_html_entities(weight_volume),
        "packaging": clean_html_entities(packaging_values),
        "additional_info": clean_html_entities(additional_info_list),
        "images": clean_html_entities(image_urls),
    }

    cache["product_details"] = product_details

    return product_details


if __name__ == "__main__":
    shop_url = 'https://www.anvibodycare.com/shop'
    product_page_links = get_product_page_links(shop_url)
    for link in product_page_links:
        print(parse_product_page(link))
