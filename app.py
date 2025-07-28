from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import os
import uuid
import logging
import re
import openpyxl

from dropbox_uploader import upload_to_dropbox

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class RequestModel(BaseModel):
    fileName: str
    data: List[Dict[str, Any]]

def sanitize_filename(filename: str) -> str:
    """Sostituisce tutti i caratteri non alfanumerici con underscore"""
    return re.sub(r"[^\w\-\.]", "_", filename)

@app.post("/upload-json/")
async def upload_json(payload: RequestModel):
    logger.info("📥 Ricevuta richiesta JSON per conversione in XLSX.")

    filepath = None

    try:
        # 1. Sanitizza nome file
        safe_name = sanitize_filename(payload.fileName)
        final_filename = f"{safe_name}_{uuid.uuid4().hex}.xlsx"
        filepath = os.path.join("/tmp", final_filename)
        logger.info(f"📄 Nome file pulito: {final_filename}")

        # 2. Conversione a DataFrame
        df = pd.DataFrame(payload.data)

        # 2.a Rimuovi simboli euro e virgole, converte numeri
for col in df.columns:
    if col == "BC":
        continue  # non toccare la colonna BC, deve restare testo

    if df[col].dtype == object:
        df[col] = df[col].str.replace("€", "", regex=False)
        df[col] = df[col].str.replace(",", ".", regex=False)
        df[col] = df[col].str.strip()
    try:
        df[col] = pd.to_numeric(df[col])
    except ValueError:
        pass

        logger.info(f"🧾 Colonne: {df.columns.tolist()}")

        # 3. Salvataggio su disco
        df.to_excel(filepath, index=False)

        # 3.a Formattazione numerica Excel (2 decimali)
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active

        for row in ws.iter_rows(min_row=2):  # salta intestazione
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '0.00'
        wb.save(filepath)

        logger.info(f"📄 File XLSX creato in: {filepath}")

        # 4. Upload a Dropbox nella cartella /mtoXLSX
        dropbox_path = f"/mtoXLSX/{final_filename}"
        response = upload_to_dropbox(filepath, dropbox_path)

        logger.info(f"✅ File caricato su Dropbox: {dropbox_path}")

        return {
            "message": "Upload completato",
            "dropbox_path": dropbox_path,
            "dropbox_response": response
        }

    except Exception as e:
        logger.error(f"❌ Errore: {str(e)}")
        return {"error": str(e)}

    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🧹 File temporaneo eliminato: {filepath}")
