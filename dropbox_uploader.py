import os
import requests
import logging
from dotenv import load_dotenv

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carica le variabili .env
load_dotenv()

DROPBOX_CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

def get_access_token():
    logger.info("🔐 Richiesta access token da Dropbox...")

    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN,
    }

    response = requests.post(
        url,
        data=data,
        auth=(DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET)
    )

    if response.ok:
        logger.info("✅ Access token ottenuto con successo.")
    else:
        logger.error(f"❌ Errore ottenendo access token: {response.text}")

    response.raise_for_status()
    return response.json()["access_token"]

def upload_to_dropbox(file_path, dropbox_path):
    logger.info(f"⬆️ Inizio upload su Dropbox: {dropbox_path}")

    access_token = get_access_token()

    with open(file_path, "rb") as f:
        data = f.read()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": str({
            "path": dropbox_path,
            "mode": "overwrite",
            "autorename": True,
            "mute": False,
            "strict_conflict": False
        }).replace("'", '"'),
        "Content-Type": "application/octet-stream"
    }

    upload_url = "https://content.dropboxapi.com/2/files/upload"
    res = requests.post(upload_url, headers=headers, data=data)

    if res.ok:
        logger.info(f"✅ Upload completato: {dropbox_path}")
    else:
        logger.error(f"❌ Errore upload: {res.text}")

    res.raise_for_status()
    return res.json()
