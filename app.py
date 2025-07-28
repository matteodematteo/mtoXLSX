from flask import Flask, request, jsonify
from dropbox_uploader import upload_to_dropbox
import pandas as pd
from io import BytesIO
from datetime import datetime
import logging

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        logging.info("✅ Webhook ricevuto")

        payload = request.get_json()
        if not payload:
            logging.warning("❌ JSON non ricevuto o vuoto")
            return jsonify({"error": "Invalid or empty JSON"}), 400

        data = payload.get("data")
        filename_base = payload.get("fileName")

        if not data or not filename_base:
            logging.warning("❌ Mancano 'data' o 'fileName'")
            return jsonify({"error": "Missing 'data' or 'fileName'"}), 400

        df = pd.DataFrame(data)
        logging.info(f"📊 Dati ricevuti: {len(df)} righe, colonne: {list(df.columns)}")

        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        filename = f"/mtoXLSX/{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        logging.info(f"📁 Nome file Dropbox: {filename}")

        success, message = upload_to_dropbox(output, filename)

        if success:
            logging.info("✅ Upload su Dropbox riuscito")
            return jsonify({"message": "File uploaded", "path": filename}), 200
        else:
            logging.error(f"❌ Errore Dropbox: {message}")
            return jsonify({"error": message}), 500

    except Exception as e:
        logging.exception("❌ Errore imprevisto")
        return jsonify({"error": str(e)}), 500
