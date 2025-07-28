from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dropbox_uploader import upload_to_dropbox
import logging
import io
from openpyxl import Workbook
import unicodedata

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def sanitize_filename(name):
    """Rimuove caratteri non ASCII e rende il nome sicuro per i file"""
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    return secure_filename(name)

@app.route('/')
def index():
    return '✅ Webhook XLSX Exporter is running!'

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        payload = request.get_json()
        logging.info("📥 Webhook ricevuto")

        filename = payload.get('fileName', 'report')
        filename = sanitize_filename(filename)
        logging.info(f"📁 Nome file: {filename}.xlsx")

        data = payload.get('data', [])

        wb = Workbook()
        ws = wb.active
        ws.title = "Export"

        # Header
        if data:
            ws.append(list(data[0].keys()))

        # Righe
        for item in data:
            ws.append(list(item.values()))

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        success, message = upload_to_dropbox(output, f"/mtoXLSX/{filename}.xlsx")
        if success:
            logging.info("✅ File caricato su Dropbox con successo")
            return jsonify({"status": "success", "message": message}), 200
        else:
            logging.error("❌ Errore nel caricamento su Dropbox")
            return jsonify({"status": "error", "message": message}), 500

    except Exception as e:
        logging.exception("❌ Errore imprevisto")
        return jsonify({"status": "error", "message": str(e)}), 500
