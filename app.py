from flask import Flask, request
import pandas as pd
from io import BytesIO
from dropbox_uploader import upload_to_dropbox
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def index():
    return "✅ Server attivo!"

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    logging.info("📥 Webhook ricevuto")

    try:
        json_data = request.get_json()
        if not json_data:
            logging.error("❌ Nessun JSON trovato nella richiesta")
            return "Bad Request", 400

        file_name = json_data.get("fileName", "output")
        data = json_data.get("data", [])

        if not data:
            logging.error("❌ Nessun dato trovato nel JSON")
            return "No data", 400

        logging.info(f"📁 Nome file: {file_name}")

        # Usa le chiavi esattamente come sono per gli header
        df = pd.DataFrame(data)

        # Scrive il file Excel in memoria
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        # Costruisci nome file .xlsx corretto (rimuove caratteri non validi da file_name)
        safe_name = "".join(c for c in file_name if c not in r'\/:*?"<>|')
        filename = f"/mtoXLSX/{safe_name}.xlsx"

        # Carica su Dropbox
        success, message = upload_to_dropbox(output, filename)
        if success:
            logging.info("✅ File caricato su Dropbox")
            return "Success", 200
        else:
            logging.error("❌ Errore nel caricamento su Dropbox")
            return message, 500

    except Exception as e:
        logging.error(f"❌ Errore imprevisto\n{e}", exc_info=True)
        return "Internal Server Error", 500
