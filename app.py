from flask import Flask, request, jsonify
from openpyxl import Workbook
from datetime import datetime
import os

app = Flask(__name__)
SAVE_FOLDER = "./generated_xlsx"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        file_name = f"{data['fileName']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        file_path = os.path.join(SAVE_FOLDER, file_name)

        wb = Workbook()
        ws = wb.active
        ws.title = "Data"

        headers = ["bc", "qt", "in", "spec", "pp", "sp", "sd1", "sd2", "sd3", "sd4"]
        ws.append(headers)

        for item in data.get("data", []):
            ws.append([item.get(k, "") for k in headers])

        wb.save(file_path)

        return jsonify({"status": "success", "saved_file": file_name})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # compatibile con Render
    app.run(host="0.0.0.0", port=port)
