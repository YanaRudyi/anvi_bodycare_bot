import csv
import requests
from bs4 import BeautifulSoup


def product_parse(url):
    response = requests.get(url)

    if response.status_code == 200:
        with open('product_data.csv', 'w', newline='', encoding='utf-8') as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow(['Product name', 'Product URL', 'Product price', 'Product IMG URL'])

            soup = BeautifulSoup(response.text, 'html.parser')
            product_containers = soup.find_all('div', {'data-hook': 'product-item-root'})

            for container in product_containers:
                product_name = container.find('h3', {'data-hook': 'product-item-name'}).text.strip()

                product_url = container.find('a', {'data-hook': 'product-item-container'})['href']

                product_price = container.find('span', {'data-hook': 'product-item-price-to-pay'}).text.strip()

                product_image_url = container.find('img')['src']

                writer.writerow([product_name, product_url, product_price, product_image_url])


product_parse('https://www.anvibodycare.com/shop')
