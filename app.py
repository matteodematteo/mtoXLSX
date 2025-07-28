import io
import logging
from flask import Flask, request, jsonify
from xlsxwriter.workbook import Workbook
from dropbox_uploader import upload_to_dropbox

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return '✅ Servizio attivo!'

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        logger.info("📥 Webhook ricevuto")

        # Ricezione JSON
        payload = request.get_json()
        if not payload or "data" not in payload or "fileName" not in payload:
            logger.error("❌ JSON mancante o incompleto")
            return jsonify({"error": "Payload non valido"}), 400

        filename = payload.get("fileName", "report")
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        logger.info(f"📁 Nome file: {filename}")

        # Generazione file Excel
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Dati")

        headers = ["barcode", "comparison qty", "name", "prod.code", "cost", "price", "disc1%", "disc2%", "disc3%", "disc4%"]
        worksheet.write_row(0, 0, headers)

        for idx, row in enumerate(payload["data"], start=1):
            worksheet.write_row(idx, 0, [
                row.get("bc", ""),
                row.get("qt", ""),
                row.get("in", ""),
                row.get("spec", ""),
                row.get("pp", ""),
                row.get("sp", ""),
                row.get("sd1", ""),
                row.get("sd2", ""),
                row.get("sd3", ""),
                row.get("sd4", "")
            ])

        workbook.close()
        output.seek(0)

        # Upload su Dropbox
        success, message = upload_to_dropbox(output, filename)
        if success:
            logger.info("✅ Upload completato")
            return jsonify({"message": "File caricato con successo", "path": message}), 200
        else:
            logger.error("❌ Errore nel caricamento su Dropbox")
            return jsonify({"error": message}), 500

    except Exception as e:
        logger.exception("❌ Errore imprevisto")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
