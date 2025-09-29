from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import os
import uuid
import logging
import re
import xlsxwriter
from io import BytesIO

from dropbox_uploader import upload_to_dropbox

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class RequestModel(BaseModel):
    fileName: str
    data: List[Dict[str, Any]]

def sanitize_filename(filename: str) -> str:
    """Rimuove i caratteri non alfanumerici, lasciando solo lettere, numeri, -, _, ."""
    return re.sub(r"[^\w\-\.]", "", filename)

def short_uid(length=5) -> str:
    """Genera un ID univoco corto"""
    return uuid.uuid4().hex[:length]

@app.post("/upload-json/")
async def upload_json(payload: RequestModel):
    logger.info("📥 Ricevuta richiesta JSON per conversione in XLSX.")

    safe_name = sanitize_filename(payload.fileName)
    final_filename = f"{safe_name}.xlsx"
    filepath = os.path.join("/tmp", final_filename)

    try:
        df = pd.DataFrame(payload.data)

        # Pulizia dati: rimuove euro, converte numeri, lascia BC e IN come testo
        for col in df.columns:
            if col in ["BC", "IN"]:
                df[col] = df[col].astype(str).str.strip()
                continue

            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace("€", "", regex=False).str.replace(",", ".", regex=False).str.strip()
                try:
                    df[col] = pd.to_numeric(df[col])
                except Exception:
                    pass

        # Scrive file XLSX in memoria con formattazione
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]

            # Formati
            format_text = workbook.add_format({'num_format': '@'})
            format_num = workbook.add_format({'num_format': '0.00'})

            # Applica formato alle intestazioni per compatibilità Excel
            for col_idx, col_name in enumerate(df.columns):
                worksheet.write(0, col_idx, col_name, format_text)

            # Applica formattazione colonna per BC e IN come testo, altre come numero
            for col_idx, col_name in enumerate(df.columns):
                if col_name in ["BC", "IN"]:
                    worksheet.set_column(col_idx, col_idx, 20, format_text)
                else:
                    worksheet.set_column(col_idx, col_idx, 20, format_num)

        # Salva su disco
        with open(filepath, "wb") as f:
            f.write(output.getvalue())

        logger.info(f"📄 File XLSX generato in: {filepath}")

        # Upload su Dropbox in /mtoXLSX
        dropbox_path = f"/mtoXLSX/{final_filename}"
        response = upload_to_dropbox(filepath, dropbox_path)
        logger.info(f"✅ Caricato su Dropbox: {dropbox_path}")

        return {
            "message": "Upload completato",
            "dropbox_path": dropbox_path,
            "dropbox_response": response
        }

    except Exception as e:
        logger.error(f"❌ Errore: {str(e)}")
        return {"error": str(e)}

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🧹 File temporaneo eliminato: {filepath}")
