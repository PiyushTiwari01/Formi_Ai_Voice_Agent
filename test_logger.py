from flask import Flask, request, jsonify
import json, os, re
from datetime import datetime
from dateutil import parser
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
LOGGED_IDS_FILE = "logged_call_ids.json"

# ✅ Load existing logged call IDs
if os.path.exists(LOGGED_IDS_FILE):
    with open(LOGGED_IDS_FILE, "r") as f:
        logged_call_ids = set(json.load(f))
else:
    logged_call_ids = set()

# ✅ Save updated call IDs
def save_logged_ids():
    with open(LOGGED_IDS_FILE, "w") as f:
        json.dump(list(logged_call_ids), f)

# ✅ Spoken number words to digits
def spoken_to_digits(spoken_text):
    digit_map = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
    }
    return ''.join([digit_map.get(word, '') for word in spoken_text.lower().split()])

# ✅ Google Sheet Logger
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
        sheet = client.open("MyInformation").sheet1
        sheet.append_row(row)
        print("✅ Data written to sheet:", row)
    except Exception as e:
        print("❌ Sheet write error:", e)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"message": "✅ Webhook is live. Use POST to send data."}), 200

    elif request.method == "POST":
        try:
            data = request.json
            call = data.get("call", {})
            call_id = call.get("call_id")
            call_status = call.get("call_status", "").lower()
            call_summary = call.get("call_analysis", {}).get("call_summary", "NA")

            # 🛑 Only log if call is ended AND summary is present
            if not call_id:
                return jsonify({"error": "Missing call_id"}), 400
            if call_status not in ["completed", "ended", "finished"]:
                return jsonify({"message": "⏸️ Call not completed yet"}), 200
            if call_summary == "NA":
                return jsonify({"message": "⏭️ Skipping — summary not ready yet."}), 200
            if call_id in logged_call_ids:
                return jsonify({"message": "⏭️ Already logged"}), 200

            transcript = call.get("transcript", "").lower()

            # Defaults
            customer_name = "NA"
            phone_number = "NA"
            room_name = "NA"
            check_in_date = "NA"
            check_out_date = "NA"
            number_of_guests = "NA"

            # Room type
            room_types = ["executive room", "deluxe room", "family suite", "studio room", "classic room"]
            room_name = next((room.title() for room in room_types if room in transcript), "NA")

            # Name
            name_match = re.search(r"(?:my name is|full name is)\s+([a-zA-Z\s]+)", transcript)
            if name_match:
                customer_name = name_match.group(1).strip().title()

            # Phone number
            phone_match = re.search(
                r'(zero|one|two|three|four|five|six|seven|eight|nine)([\s\-.,]*(zero|one|two|three|four|five|six|seven|eight|nine)){9,}',
                transcript
            )
            if phone_match:
                phone_number = spoken_to_digits(phone_match.group(0))

            # Check-in / check-out
            date_match = re.search(r"check in on (\w+ \d+)[\s\S]+?check out on (\w+ \d+)", transcript)
            if date_match:
                try:
                    check_in_date = str(parser.parse(date_match.group(1)).date())
                    check_out_date = str(parser.parse(date_match.group(2)).date())
                except:
                    check_in_date = date_match.group(1)
                    check_out_date = date_match.group(2)

            # Guests
            guest_match = re.search(r"(\d+)\s+(guests|guest)", transcript)
            if guest_match:
                number_of_guests = guest_match.group(1)
            else:
                word_match = re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b", transcript)
                if word_match:
                    spoken_map = {
                        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
                        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
                    }
                    number_of_guests = spoken_map.get(word_match.group(1).lower(), "NA")

            # Final data
            log_data = {
                "call_id": call_id,
                "call_time": call.get("call_start_time", "NA"),
                "phone_number": phone_number,
                "customer_name": customer_name,
                "room_name": room_name,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "number_of_guests": number_of_guests,
                "call_outcome": call_status,
                "call_summary": call_summary,
                "raw_transcript": transcript
            }

            log_to_sheet(log_data)
            logged_call_ids.add(call_id)
            save_logged_ids()

            return jsonify({"message": "✅ Final data logged"}), 200

        except Exception as e:
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/webhook-status", methods=["GET"])
def webhook_status():
    return jsonify({"message": "✅ Webhook server is running"}), 200

@app.route("/webhook/<call_id>", methods=["GET"])
def get_call_info(call_id):
    if call_id in logged_call_ids:
        return jsonify({"message": f"✅ Data for call_id '{call_id}' has been logged."}), 200
    else:
        return jsonify({"message": f"❌ No data found for call_id '{call_id}'"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
