# google_sheets_logger.py
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def log_to_sheet(log_data):
    print("📝 Logging to Google Sheet (final):")
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        log_data.get("call_id", "NA"),
        log_data.get("phone_number", "NA"),
        log_data.get("customer_name", "NA"),
        log_data.get("room_name", "NA"),
        log_data.get("check_in_date", "NA"),
        log_data.get("check_out_date", "NA"),
        log_data.get("number_of_guests", "NA"),
        log_data.get("call_outcome", "NA"),
        log_data.get("call_summary", "NA")
    ]
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("MyInformation").sheet1  # ✅ Must match actual sheet title
        sheet.append_row(row)
        print("✅ Data written to sheet:", row)
    except Exception as e:
        print("❌ Sheet write error:", e)



#  Step 1: Set Up Google Sheets API Access
# 1.1. Go to Google Cloud Console
# Visit: https://console.cloud.google.com/

# Create a new project (or use an existing one)

# 1.2. Enable APIs
# Go to APIs & Services > Library

# Enable Google Sheets API

# Enable Google Drive API (required for file access)

# 1.3. Create Service Account
# Go to APIs & Services > Credentials

# Click Create Credentials > Service Account

# Give it a name (e.g., sheets-service-account)

# Go to "Keys" tab of the created account

# Click Add Key > JSON

# Save the JSON file (you’ll use it in the Flask app)

# ✅ Step 2: Share the Sheet with the Service Account
# Open your Google Sheet (create one if not already).

# Click Share

# Copy the email address from the JSON file (e.g., sheets-api@your-project.iam.gserviceaccount.com)

# Share the sheet with Editor access to that email.

# ✅ Step 3: Install Required Python Packages
# bash
# Copy
# Edit
# pip install gspread oauth2client
# 🔐 Place your credentials.json file in the project directory.






# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # ✅ Setup Google Sheets connection
# def get_google_sheet():
#     scope = ['https://spreadsheets.google.com/feeds',
#              'https://www.googleapis.com/auth/drive']
#     creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#     client = gspread.authorize(creds)

#     # Replace with your actual sheet name
#     sheet = client.open("Voice AI Call Logs").sheet1
#     return sheet


# def log_to_sheet(log_data):
#     print("📝 Logging to Google Sheet (final):", log_data)
#     row = [
#         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         log_data.get("call_id", "NA"),
#         log_data.get("phone_number", ""),
#         log_data.get("customer_name", ""),
#         log_data.get("room_name", ""),
#         log_data.get("check_in_date", ""),
#         log_data.get("check_out_date", ""),
#         log_data.get("number_of_guests", ""),
#         log_data.get("call_outcome", ""),
#         log_data.get("call_summary", "")
#     ]
#     print("➡️ Row to insert:", row)

#     # ✅ Append row to Google Sheet
#     try:
#         sheet = get_google_sheet()
#         sheet.append_row(row)
#         print("✅ Data successfully written to Google Sheet.")
#     except Exception as e:
#         print("❌ Failed to log to Google Sheet:", str(e))
