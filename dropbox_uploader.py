import requests
import json
import logging

DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"
DROPBOX_TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"

def upload_to_dropbox(file_stream, dropbox_path, access_token):
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({
                "path": dropbox_path,
                "mode": "add",          # Non sovrascrivere, crea nuova versione con nome unico
                "autorename": True,     # Abilita rename automatico
                "mute": False
            })
        }
        response = requests.post(DROPBOX_UPLOAD_URL, headers=headers, data=file_stream)
        if response.status_code == 200:
            logging.info(f"✅ Upload completato: {dropbox_path}")
            return True, "Upload completato"
        else:
            logging.error(f"❌ Errore nell'upload su Dropbox: {response.status_code} - {response.text}")
            return False, f"Errore upload: {response.status_code} - {response.text}"
    except Exception as e:
        logging.error(f"❌ Errore imprevisto: {e}")
        return False, str(e)

def get_access_token(refresh_token, client_id, client_secret):
    try:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        response = requests.post(DROPBOX_TOKEN_URL, data=data)
        response.raise_for_status()
        token_json = response.json()
        return token_json.get("access_token")
    except Exception as e:
        logging.error(f"❌ Errore ottenimento access token: {e}")
        return None
