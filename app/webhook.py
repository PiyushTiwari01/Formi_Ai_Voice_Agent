# from flask import Flask, request, jsonify
# from app.utils.sheet_logger import log_to_sheet

# app = Flask(__name__)

# @app.route('/webhook', methods=['POST'])
# def receive_call_data():
#     data = request.json
#     user_name = data.get('name')
#     user_query = data.get('question')
#     ai_response = data.get('answer')
#     status = data.get('status')

#     # Log to Google Sheet
#     log_to_sheet(user_name, user_query, ai_response, status)
#     return jsonify({"message": "Data logged successfully"}), 200

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)
