import requests
import logging
import os
from io import BytesIO

DROPBOX_CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

DROPBOX_TOKEN_URL = "https://api.dropbox.com/oauth2/token"
DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"

def get_access_token():
    """Ottiene un access token usando il refresh token."""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN,
        "client_id": DROPBOX_CLIENT_ID,
        "client_secret": DROPBOX_CLIENT_SECRET
    }
    try:
        response = requests.post(DROPBOX_TOKEN_URL, data=data)
        response.raise_for_status()
        token_json = response.json()
        return token_json.get("access_token")
    except Exception as e:
        logging.error(f"Errore ottenimento access token: {str(e)}")
        return None

def upload_to_dropbox(file_stream, filename):
    access_token = get_access_token()
    if not access_token:
        return False, "Impossibile ottenere access token Dropbox"

    dropbox_path = f"/mtoXLSX/{filename}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f'{{"path": "{dropbox_path}", "mode": "overwrite", "autorename": false, "mute": false}}'
    }

    try:
        response = requests.post(DROPBOX_UPLOAD_URL, headers=headers, data=file_stream)
        if response.status_code == 200:
            return True, "Upload completato"
        else:
            logging.error(f"Errore upload Dropbox: {response.status_code} - {response.text}")
            return False, response.text
    except Exception as e:
        logging.error(f"Errore imprevisto: {str(e)}")
        return False, str(e)
