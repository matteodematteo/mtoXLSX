from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import os
import uuid
import logging
import re

from dropbox_uploader import upload_to_dropbox

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class RequestModel(BaseModel):
    fileName: str
    data: List[Dict[str, Any]]

def sanitize_filename(filename: str) -> str:
    """Sostituisce tutti i caratteri non alfanumerici con underscore"""
    sanitized = re.sub(r"[^\w\-\.]", "_", filename)
    return sanitized

@app.post("/upload-json/")
async def upload_json(payload: RequestModel):
    logger.info("📥 Ricevuta richiesta JSON per conversione in XLSX.")

    try:
        # 1. Sanitizza nome file
        original_name = payload.fileName
        safe_name = sanitize_filename(original_name)
        final_filename = f"{safe_name}_{uuid.uuid4().hex}.xlsx"
        filepath = os.path.join("/tmp", final_filename)
        logger.info(f"📄 Nome file pulito: {final_filename}")

        # 2. Conversione a DataFrame
        df = pd.DataFrame(payload.data)
        logger.info(f"🧾 Header colonne: {df.columns.tolist()}")

        # 3. Salvataggio su disco
        df.to_excel(filepath, index=False)
        logger.info(f"📄 File XLSX creato in: {filepath}")

        # 4. Upload a Dropbox
        dropbox_path = f"/{final_filename}"
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
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🧹 File temporaneo eliminato: {filepath}")
