import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
import gspread
import pandas as pd
from src.env import config
from google.cloud import secretmanager

MODE = config("MODE", cast=str, default="test")
import json

SERVICE_ACCOUNT_CREDS = json.loads(config("GOOGLE_CREDENTIALS", default="{}"))

# with open("service_account.json", "w") as f:
#     f.write(SERVICE_ACCOUNT_CREDS)

app = FastAPI()

# Set up Google Sheets API credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def authenticate_google_sheets():
    return gspread.service_account_from_dict(SERVICE_ACCOUNT_CREDS)

def get_worksheet_data(sh, worksheet_index, ranges):
    """Get data from specified ranges in a worksheet."""
    worksheet = sh.get_worksheet(worksheet_index)
    return worksheet.batch_get(ranges)

def list_to_dataframe(data):
    """Convert list of lists to DataFrame with the first list as column headers."""
    if data:
        return pd.DataFrame(data[1:], columns=data[0])
    else:
        return pd.DataFrame()

@app.get("/")
def home_page():
    return {"Hello": "World", "mode": MODE}

@app.get("/get-data")
def get_data():
    gc = authenticate_google_sheets()
    sh = gc.open_by_key("10cCshBXUSnu5hHUvnc5CPCrJOeZlZaMtHPaZOx2M950")

    raw_ref_main = get_worksheet_data(sh, 0, ['B7:I22', 'K7:O8', 'Q7:T13'])
    raw_ref_main_test = get_worksheet_data(sh, 10, ['A1:G2'])
    raw_ref = get_worksheet_data(sh, 1, ['B2:C7', 'E2:F9', 'H2:P53', 'R2:S28', 'U2:V7', 'X2:Z6'])

    df_Keyway_Description = list_to_dataframe(raw_ref[0])
    df_Thard_Operations = list_to_dataframe(raw_ref[1])
    df_ops_metadata = list_to_dataframe(raw_ref[2])
    df_operations = list_to_dataframe(raw_ref[3])
    df_operator = list_to_dataframe(raw_ref[4])
    df_Workstation = list_to_dataframe(raw_ref[5])

    df_main = list_to_dataframe(raw_ref_main_test[0])
    df_main_step_description = list_to_dataframe(raw_ref_main[0])
    df_main_keyway_description = list_to_dataframe(raw_ref_main[1])
    df_main_finish_description = list_to_dataframe(raw_ref_main[2])

    worksheet_drawing = sh.get_worksheet(2)
    df_main_drawing = pd.DataFrame(worksheet_drawing.get_all_records())

    worksheet_step = sh.get_worksheet(3)
    df_main_step = pd.DataFrame(worksheet_step.get_all_records())

    worksheet_keyway = sh.get_worksheet(4)
    df_main_keyway = pd.DataFrame(worksheet_keyway.get_all_records())

    worksheet_finish = sh.get_worksheet(5)
    df_main_finish = pd.DataFrame(worksheet_finish.get_all_records())

    worksheet_calc = sh.get_worksheet(6)
    raw_ref_calc = worksheet_calc.batch_get(['CE7:CJ29'])
    df_main_calc = list_to_dataframe(raw_ref_calc[0])

    data = {
        "df_main": df_main.to_dict(orient="records"),
        "df_main_step_description": df_main_step_description.to_dict(orient="records"),
        "df_main_keyway_description": df_main_keyway_description.to_dict(orient="records"),
        "df_main_finish_description": df_main_finish_description.to_dict(orient="records"),
        "df_main_drawing": df_main_drawing.to_dict(orient="records"),
        "df_main_step": df_main_step.to_dict(orient="records"),
        "df_main_keyway": df_main_keyway.to_dict(orient="records"),
        "df_main_finish": df_main_finish.to_dict(orient="records"),
        "df_Keyway_Description": df_Keyway_Description.to_dict(orient="records"),
        "df_Thard_Operations": df_Thard_Operations.to_dict(orient="records"),
        "df_ops_metadata": df_ops_metadata.to_dict(orient="records"),
        "df_operations": df_operations.to_dict(orient="records"),
        "df_operator": df_operator.to_dict(orient="records"),
        "df_Workstation": df_Workstation.to_dict(orient="records"),
        "df_main_calc": df_main_calc.to_dict(orient="records"),
    }

    return JSONResponse(content=data)
