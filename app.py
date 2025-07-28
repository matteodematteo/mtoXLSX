from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import os
import uuid
import logging
import re

from dropbox_uploader import upload_to_dropbox  # Make sure this file exists separately

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class RequestModel(BaseModel):
    fileName: str
    data: List[Dict[str, Any]]


def sanitize_filename(filename: str) -> str:
    """Replace all non-alphanumeric characters with underscores"""
    return re.sub(r"[^\w\-\.]", "_", filename)


@app.post("/upload-json/")
async def upload_json(payload: RequestModel):
    logger.info("📥 JSON received for XLSX conversion.")

    filepath = None  # Initialize to avoid reference before assignment

    try:
        # 1. Sanitize filename
        safe_name = sanitize_filename(payload.fileName)
        final_filename = f"{safe_name}_{uuid.uuid4().hex}.xlsx"
        filepath = os.path.join("/tmp", final_filename)
        logger.info(f"📄 Clean filename: {final_filename}")

        # 2. Convert to DataFrame
        df = pd.DataFrame(payload.data)
        logger.info(f"🧾 Columns: {df.columns.tolist()}")

        # 3. Save to disk
        df.to_excel(filepath, index=False)
        logger.info(f"📄 XLSX file saved to: {filepath}")

        # 4. Upload to Dropbox
        dropbox_path = f"/mtoXLSX/{final_filename}"
        response = upload_to_dropbox(filepath, dropbox_path)

        logger.info(f"✅ File uploaded to Dropbox: {dropbox_path}")

        return {
            "message": "Upload complete",
            "dropbox_path": dropbox_path,
            "dropbox_response": response
        }

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return {"error": str(e)}

    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🧹 Temp file deleted: {filepath}")
