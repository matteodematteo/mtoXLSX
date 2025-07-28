import requests
import json
import logging

# Inserisci i tuoi dati qui
REFRESH_TOKEN = "IL_TUO_REFRESH_TOKEN"
CLIENT_ID = "IL_TUO_CLIENT_ID"
CLIENT_SECRET = "IL_TUO_CLIENT_SECRET"

DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"
DROPBOX_TOKEN_URL = "https://api.dropbox.com/oauth2/token"

def get_access_token(refresh_token, client_id, client_secret):
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        response = requests.post(DROPBOX_TOKEN_URL, data=data)
        response.raise_for_status()
        token = response.json().get("access_token")
        logging.info("✅ Access token ottenuto correttamente.")
        return token
    except Exception as e:
        logging.error(f"❌ Errore nel recupero access token: {e}")
        return None

def upload_to_dropbox(file_stream, filename, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps({
            "path": filename,
            "mode": "add",          # add per non sovrascrivere, autorename automatico
            "autorename": True,
            "mute": False,
            "strict_conflict": False
        })
    }
    try:
        file_stream.seek(0)
        response = requests.post(DROPBOX_UPLOAD_URL, headers=headers, data=file_stream.read())
        if response.status_code == 200:
            logging.info(f"✅ File caricato correttamente: {filename}")
            return True, "Upload completato"
        else:
            logging.error(f"❌ Errore nell'upload su Dropbox: {response.status_code} - {response.text}")
            return False, f"Errore {response.status_code}: {response.text}"
    except Exception as e:
        logging.error(f"❌ Errore imprevisto durante upload: {e}")
        return False, str(e)
