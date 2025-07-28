import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

DROPBOX_FOLDER = "/mtoXLSX"

def get_access_token():
    logger.info("🔄 Richiesta access token da Dropbox...")
    refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    client_id = os.getenv("DROPBOX_CLIENT_ID")
    client_secret = os.getenv("DROPBOX_CLIENT_SECRET")

    token_url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(token_url, data=data, auth=(client_id, client_secret))
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logger.info("✅ Access token ottenuto correttamente.")
        return access_token
    except Exception as e:
        logger.error("❌ Errore nel recupero access token da Dropbox")
        raise e

def upload_to_dropbox(file_stream, filename):
    logger.info(f"📁 Upload in corso su Dropbox: {DROPBOX_FOLDER}/{filename}")
    upload_url = "https://content.dropboxapi.com/2/files/upload"
    dropbox_path = f"{DROPBOX_FOLDER}/{filename}"

    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Dropbox-API-Arg": json.dumps({
            "path": dropbox_path,
            "mode": "overwrite",
            "autorename": False,
            "mute": False,
            "strict_conflict": False
        }),
        "Content-Type": "application/octet-stream"
    }

    try:
        response = requests.post(upload_url, headers=headers, data=file_stream.read())
        response.raise_for_status()
        logger.info(f"✅ Upload Dropbox completato: {dropbox_path}")
        return True, dropbox_path
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Errore nell'upload su Dropbox: {e}")
        return False, str(e)
