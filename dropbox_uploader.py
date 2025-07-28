import os
import requests
import logging

DROPBOX_CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"
DROPBOX_TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"

def get_access_token():
    logging.info("🔄 Richiesta access token da Dropbox...")

    response = requests.post(
        DROPBOX_TOKEN_URL,
        data={"grant_type": "refresh_token", "refresh_token": DROPBOX_REFRESH_TOKEN},
        auth=(DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET)
    )

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        logging.info("✅ Access token ottenuto correttamente.")
        return access_token
    else:
        logging.error(f"❌ Errore nell'ottenimento dell'access token: {response.text}")
        return None

def upload_to_dropbox(file_stream, dropbox_path):
    access_token = get_access_token()
    if not access_token:
        return False, "Access token non ottenuto"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": str({
            "path": dropbox_path,
            "mode": "add",
            "autorename": True,
            "mute": False,
            "strict_conflict": False
        }).replace("'", '"')  # Dropbox richiede JSON con doppi apici
    }

    logging.info(f"📁 Upload in corso su Dropbox: {dropbox_path}")

    response = requests.post(DROPBOX_UPLOAD_URL, headers=headers, data=file_stream)

    if response.status_code == 200:
        return True, "Caricamento completato"
    else:
        logging.error(f"❌ Errore nell'upload su Dropbox: {response.status_code} - {response.text}")
        return False, response.text
