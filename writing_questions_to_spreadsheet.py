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
        range='Data',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    return result
