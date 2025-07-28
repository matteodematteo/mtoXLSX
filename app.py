from flask import Flask, request, jsonify
from openpyxl import Workbook
from datetime import datetime
import os

app = Flask(__name__)
SAVE_FOLDER = "./generated_xlsx"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "OK",
        "message": "✅ Server attivo ed esistente!"
    }), 200

@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "app": "XLSX-Uploader",
        "version": "1.0.0",
        "description": "Servizio per ricevere dati JSON e salvare file Excel"
    }), 200

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
            row = [item.get(k, "") for k in headers]
            ws.append(row)

        wb.save(file_path)

        return jsonify({
            "status": "success",
            "message": f"✅ File salvato correttamente: {file_name}",
            "file_path": file_path
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"❌ Errore durante la generazione del file: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Avvio su porta {port}...")
    app.run(host="0.0.0.0", port=port)
