import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

def log_to_sheet(user_name, user_query, ai_response, status):
    # Define scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Path to your JSON key file (make sure it's correct)
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open your spreadsheet (replace with your sheet name)
    sheet = client.open("MyInformation").sheet1


    # Current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Data to insert
    row = [timestamp, user_name, user_query, ai_response, status]

    # Append the row to the sheet
    sheet.append_row(row)

    print("✅ Data logged to sheet successfully!")
