from flask import Flask, request, jsonify

app = Flask(__name__)
logged_call_ids = set()

# Simulated Google Sheet logger
def log_to_sheet(log_data):
    print("📝 Logging to Google Sheet (final):")
    for key, value in log_data.items():
        print(f"   {key}: {value}")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"message": "✅ Webhook is live. Use POST to send data."}), 200

    elif request.method == "POST":
        try:
            data = request.json
            print("👉 Incoming POST data:", data)

            call = data.get("call", {})
            variables = call.get("variables", {})
            call_id = call.get("call_id", None)
            call_status = call.get("call_status", "NA").lower()

            # 🚫 If call not ended, skip
            if call_status not in ["completed", "ended", "finished"]:
                print(f"⏸️ Skipping log: call not completed yet (status = {call_status})")
                return jsonify({"message": "Call not completed yet. Skipping log."}), 200

            if not call_id:
                return jsonify({"error": "Missing call_id"}), 400

            if call_id in logged_call_ids:
                print(f"⚠️ Already logged: call_id {call_id}")
                return jsonify({"message": "⏭️ Already logged"}), 200

            log_data = {
                "call_time": call.get("call_start_time", "NA"),
                "phone_number": call.get("phone_number", "NA"),
                "call_outcome": call_status,
                "customer_name": call.get("agent_name", "NA"),
                "room_name": variables.get("room_name", "NA"),
                "check_in_date": variables.get("check_in_date", "NA"),
                "check_out_date": variables.get("check_out_date", "NA"),
                "number_of_guests": variables.get("number_of_guests", "NA"),
                "call_summary": call.get("call_analysis", {}).get("call_summary", "NA")
            }

            log_to_sheet(log_data)
            logged_call_ids.add(call_id)
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
