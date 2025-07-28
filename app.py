import io
import logging
from flask import Flask, request, jsonify
from dropbox_uploader import upload_to_dropbox
import pandas as pd

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    logging.info("📥 Webhook ricevuto")

    # Qui dovresti ricevere i dati JSON da AppSheet o simili
    data = request.get_json()
    # Esempio: estrai dati da "data" e crea un DataFrame pandas
    # Qui va la tua logica di trasformazione dati
    df = pd.DataFrame(data.get("data", []))

    # Crea un file Excel in memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Scrivi i dati nel foglio "Sheet1"
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)

    filename = "fileMTO.xlsx"  # Nome fisso

    logging.info(f"📁 Nome file: {filename}")
    success, message = upload_to_dropbox(output, filename)
    if success:
        logging.info("✅ File caricato con successo su Dropbox")
        return jsonify({"status": "ok"})
    else:
        logging.error(f"❌ Errore nel caricamento su Dropbox: {message}")
        return jsonify({"status": "error", "message": message}), 500

if __name__ == "__main__":
    app.run(debug=True)
