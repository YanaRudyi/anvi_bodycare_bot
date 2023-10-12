import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime

spreadsheet_id = '1fqqDQZvW9IeLCW1mA2k1H2pAPvdfVpl_M5lNWswtGjs'

credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')

credentials_dict = json.loads(credentials_json)

creds = service_account.Credentials.from_service_account_info(
    credentials_dict, scopes=['https://www.googleapis.com/auth/spreadsheets']
)

service = build('sheets', 'v4', credentials=creds)


def write_to_spreadsheet(help_info):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    values = [[current_time, help_info['first_name'], help_info['phone_number'], help_info['message']]]
    body = {'values': values}

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='Messages',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    return result


def write_order_to_spreadsheet(order_info, shopping_cart):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order_items = []
    for item in shopping_cart:
        product_name = item.get('product name', '')
        weight_option = item.get('weight option', '')
        packaging_option = item.get('packaging option', '')
        product_price = item.get('product price', 0)

        item_description = f"{product_name}"
        if weight_option:
            item_description += f" ({weight_option}"
        if packaging_option:
            if weight_option:
                item_description += f", {packaging_option}"
            else:
                item_description += f" ({packaging_option}"
        item_description += f") - {product_price} грн"

        order_items.append(item_description)

    cart_items_str = ', '.join(order_items)

    values = [[
        current_time,
        order_info['first_name'],
        order_info['phone_number'],
        cart_items_str,
        order_info['message']
    ]]

    body = {'values': values}

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='Orders',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    return result
