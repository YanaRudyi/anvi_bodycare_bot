import requests
from bs4 import BeautifulSoup
import json


def get_product_page_links(shop_url):
    product_page_links = set()

    response = requests.get(shop_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_links = soup.find_all('a', href=True)

        for link in product_links:
            product_page_url = link['href']
            if 'product-page' in product_page_url:
                product_page_links.add(product_page_url)

        return product_page_links
    else:
        print(f"Failed to retrieve shop page: {shop_url}")
        return set()


def parse_product_page(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", {
            "type": "application/json",
            "id": "wix-warmup-data",
            }
            )

        if script_tag:
            json_data = json.loads(script_tag.string)

            dynamic_key = None

            for key in json_data.get("appsWarmupData", {}).get(
                    "1380b703-ce81-ff05-f115-39571d94dfcd", {}):
                if key.startswith("productPage_UAH_"):
                    dynamic_key = key
                    break
            json_path = json_data.get("appsWarmupData", {}).get(
                "1380b703-ce81-ff05-f115-39571d94dfcd", {}).get(
                dynamic_key, {}).get(
                "catalog").get(
                "product", {}).get

            product_name = json_path("name")

            description = json_path("description")

            product_items = json_path("productItems", [])
            formatted_prices = [item.get("formattedPrice") for
                                item in product_items]

            options_list = json_path("options", [])
            weight_volume = []
            for option in options_list[:1]:
                if "selections" in option and isinstance(
                        option["selections"], list):
                    for selection in option["selections"]:
                        if "key" in selection:
                            weight_volume.append(selection["key"])

            packaging_options_list = json_path("options", [])
            packaging_values = []
            if len(packaging_options_list) > 1:
                second_option = packaging_options_list[1]
                if "selections" in second_option and isinstance(
                        second_option["selections"], list):
                    for selection in second_option["selections"]:
                        if "value" in selection:
                            packaging_values.append(selection["value"])

            additional_info_list = json_path("additionalInfo", [])
            for info in additional_info_list:
                info.pop("id", None)
                info.pop("index", None)

            inner_dict = {
                "description": description,
                "prices": formatted_prices,
                "weight_volume": weight_volume,
                "packaging": packaging_values,
                "additional_info": additional_info_list,
            }

            output_dict = {product_name: inner_dict}

            output_json = json.dumps(output_dict, ensure_ascii=False, indent=4)

            return output_json
        else:
            return f'Script tag not found.'


if __name__ == "__main__":
    shop_url = 'https://www.anvibodycare.com/shop'
    output_filename = 'product_data.json'

    product_page_links = get_product_page_links(shop_url)

    if product_page_links:
        product_data_dict = {}

        for link in product_page_links:
            product_data = parse_product_page(link)
            if product_data:
                product_data_dict.update(json.loads(product_data))

        with open(output_filename, 'w', encoding='utf-8') as output_file:
            output_json = json.dumps(
                product_data_dict, 
                ensure_ascii=False, 
                indent=4,
                )
            output_file.write(output_json)

        print(
            f"Data has been written to '{output_filename}'."
            )
    else:
        print("No product-page links found on the shop page.")
