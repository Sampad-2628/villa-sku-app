import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import json

def connect_to_gsheet(sheet_name):
    # Load credentials from Streamlit Secrets
    creds_dict = st.secrets["GOOGLE_SHEET_CREDS"]
    creds_json = json.loads(json.dumps(creds_dict))  # Convert TOML-like to JSON dict
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def read_sheet_as_df(sheet):
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def append_row(sheet, row_dict):
    values = [row_dict[k] for k in row_dict]
    sheet.append_row(values)

def get_existing_sku_codes(sheet):
    data = sheet.get_all_records()
    return set(row["SKU Name Code"] for row in data if "SKU Name Code" in row)

def generate_sku_code(name, existing_codes):
    name_parts = name.strip().upper().split()

    if len(name_parts) == 1:
        base_code = name_parts[0][:2]
    elif len(name_parts) == 2:
        base_code = name_parts[0][0] + name_parts[1][0]
    else:
        base_code = name_parts[0][0] + name_parts[-1][0]

    if base_code in existing_codes:
        return None, base_code
    return base_code, None
