import re
import json
from bs4 import BeautifulSoup
import requests
import cachetools


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


cache = cachetools.TTLCache(maxsize=1, ttl=3600)


def parse_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_name = extract_product_name(soup)
    weight_options = extract_weight_options(url)
    packaging_options = extract_packaging_options(url)
    prices = extract_pricing_options(url)
    image_link = extract_image_link(soup)
    description = extract_product_description(url)

    cleaned_description = clean_html(description)

    product_details = {
        "product name": product_name,
        "images": image_link,
        "packaging options": packaging_options,
        "weight options": weight_options,
        "price": prices,
        "description": cleaned_description
    }

    cache["product_details"] = product_details

    return product_details


def extract_product_name(soup):
    product_name_element = soup.find("h1", class_="product_title")
    if product_name_element:
        return product_name_element.text.strip()
    else:
        return None


def extract_weight_options(webpage_url):
    response = requests.get(webpage_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    select_element = soup.find('select', {'name': 'attribute_pa_vaha'})
    if not select_element:
        return None
    option_elements = select_element.find_all('option')
    weight_options = [
        option.text.strip()
        for option in option_elements
        if option.text.strip() != 'Виберіть опцію'
    ]
    return weight_options


def extract_packaging_options(webpage_url):
    response = requests.get(webpage_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    option_elements = soup.select('select[name="attribute_pa_pakuvannia"] option')
    packaging_options = [
        option.text.strip()
        for option in option_elements
        if option.text.strip() != 'Виберіть опцію'
    ]

    if not packaging_options:
        return None
    return packaging_options


def extract_pricing_options(webpage_url):
    response = requests.get(webpage_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pricing_options = []

    price_element = soup.find('span', class_='woocommerce-Price-amount amount')

    if price_element:
        price_text = price_element.get_text(strip=True)
        pricing_options.append(price_text)

    form_element = soup.find('form', class_='variations_form')

    if form_element:
        product_variations = form_element.get('data-product_variations')

        if product_variations:
            variations_data = json.loads(product_variations)

            for variation in variations_data:
                option_text = variation.get('attributes', {}).get('attribute_pa_vaha', '')
                pakuvannia_text = variation.get('attributes', {}).get('attribute_pa_pakuvannia', '')
                price_html = variation.get('price_html', '')

                if option_text and price_html and pakuvannia_text:
                    price_match = re.search(r'([\d.,]+)', price_html)
                    if price_match:
                        price_text = price_match.group(1)
                        pricing_options.append([option_text, pakuvannia_text, price_text])

    return pricing_options


def extract_image_link(soup):
    image_element = soup.find("img", class_="wp-post-image")
    if image_element and "src" in image_element.attrs:
        return image_element["src"]
    else:
        return None


def extract_product_description(webpage_url):
    response = requests.get(webpage_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    description_element = soup.find('div', class_='woo-product-desc-block')
    if description_element:
        description = str(description_element)
        return description.strip()
    else:
        return None


def clean_html(raw_html):
    tag_replacements = {
        r'&nbsp;': ' ',
        r'<\/p>|<\/li>|<br>': '\n',
        r'<li>': '\n🌿 ',
        r'<strong>|<\/strong>|<p>|<ul>|<\/ul>|<u>|<\/u>': '',
        r'<[^>]*>': '',
    }

    for tag, replacement in tag_replacements.items():
        raw_html = re.sub(tag, replacement, raw_html)

    return raw_html.strip()


if __name__ == "__main__":
    shop_url = 'https://www.anvibodycare.com/shop'
    product_page_links = get_product_page_links(shop_url)
    for link in product_page_links:
        print(parse_product_page(link))
