from flask import Flask, request, jsonify
import json
import os
import re
from datetime import datetime
from dateutil import parser  # Make sure to install: pip install python-dateutil

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

# ✅ Replace this with your actual Google Sheet logging logic
def log_to_sheet(log_data):
    print("📝 Logging to Google Sheet (final):", log_data)
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        log_data.get("call_id", "NA"),
        log_data.get("phone_number", ""),
        log_data.get("customer_name", ""),
        log_data.get("room_name", ""),
        log_data.get("check_in_date", ""),
        log_data.get("check_out_date", ""),
        log_data.get("number_of_guests", ""),
        log_data.get("call_outcome", ""),
        log_data.get("call_summary", "")
    ]
    print("➡️ Row to insert:", row)
    # 👉 Insert into Google Sheets here
    # sheet.append_row(row)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"message": "✅ Webhook is live. Use POST to send data."}), 200

    elif request.method == "POST":
        try:
            data = request.json
            print("👉 Incoming POST data:", data)

            call = data.get("call", {})
            call_id = call.get("call_id", None)
            call_status = call.get("call_status", "NA").lower()

            if call_status not in ["completed", "ended", "finished"]:
                print(f"⏸️ Skipping log: call not completed yet (status = {call_status})")
                return jsonify({"message": "Call not completed yet. Skipping log."}), 200

            if not call_id:
                return jsonify({"error": "Missing call_id"}), 400

            if call_id in logged_call_ids:
                print(f"⚠️ Already logged: call_id {call_id}")
                return jsonify({"message": "⏭️ Already logged"}), 200

            transcript = call.get("transcript", "").lower()
            print("📋 Transcript:", transcript)

            # Default values
            customer_name = "NA"
            room_name = "NA"
            check_in_date = "NA"
            check_out_date = "NA"
            number_of_guests = "NA"

            # ✅ Extract customer name
            name_match = re.search(r"my name is ([a-zA-Z\s]+)", transcript)
            customer_name = name_match.group(1).title().strip() if name_match else "NA"

            # ✅ Extract room name
            room_types = ["executive room", "deluxe room", "family suite", "studio room", "classic room"]
            room_name = next((room.title() for room in room_types if room in transcript), "NA")

            # ✅ Extract check-in date
            check_in_match = re.search(r"check[-\s]?in date is ([\w\s\d/-]+)", transcript)
            if check_in_match:
                try:
                    check_in_date = str(parser.parse(check_in_match.group(1)).date())
                except:
                    check_in_date = check_in_match.group(1).strip()

            # ✅ Extract check-out date
            check_out_match = re.search(r"check[-\s]?out date is ([\w\s\d/-]+)", transcript)
            if check_out_match:
                try:
                    check_out_date = str(parser.parse(check_out_match.group(1)).date())
                except:
                    check_out_date = check_out_match.group(1).strip()

            # ✅ Extract number of guests
            guest_match = re.search(r"(\d+)\s+(guests|guest)", transcript)
            number_of_guests = guest_match.group(1) if guest_match else "NA"

            # ✅ Prepare log data
            log_data = {
                "call_id": call_id,
                "call_time": call.get("call_start_time", "NA"),
                "phone_number": call.get("phone_number", "NA"),
                "call_outcome": call_status,
                "customer_name": customer_name,
                "room_name": room_name,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "number_of_guests": number_of_guests,
                "call_summary": call.get("call_analysis", {}).get("call_summary", "NA"),
                "raw_transcript": transcript  # Optional, for debugging/log auditing
            }

            # ✅ Log the data
            log_to_sheet(log_data)

            # Save the call_id
            logged_call_ids.add(call_id)
            save_logged_ids()

            return jsonify({"message": "✅ Final data logged"}), 200

        except Exception as e:
            print("❌ Error:", str(e))
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
