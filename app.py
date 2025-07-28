from flask import Flask, request, jsonify
import io
import logging
from dropboxuploader import upload_to_dropbox, get_access_token, REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET
import openpyxl
from openpyxl import Workbook

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def genera_excel(data):
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(["bc","qt","in","spec","pp","sp","sd1","sd2","sd3","sd4"])  # header fissi

    for r in data:
        ws.append([
            r.get("bc",""),
            r.get("qt",""),
            r.get("in",""),
            r.get("spec",""),
            r.get("pp",""),
            r.get("sp",""),
            r.get("sd1",""),
            r.get("sd2",""),
            r.get("sd3",""),
            r.get("sd4","")
        ])
    file_stream = io.BytesIO()
    wb.save(file_stream)
    return file_stream

@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info("📥 Webhook ricevuto")
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No JSON payload received"}), 400

    data = json_data.get("data", [])
    if not data:
        return jsonify({"error": "No data found in payload"}), 400

    filename = "/mtoXLSX/fileMTO.xlsx"  # nome fisso con autorename in upload

    try:
        file_stream = genera_excel(data)
        access_token = get_access_token(REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET)
        if not access_token:
            return jsonify({"error": "Failed to get access token"}), 500

        success, message = upload_to_dropbox(file_stream, filename, access_token)
        if success:
            return jsonify({"status": "success", "message": message})
        else:
            return jsonify({"status": "error", "message": message}), 500

    except Exception as e:
        logging.error(f"❌ Eccezione durante elaborazione webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
