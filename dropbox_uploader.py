import requests
import logging
import os

# 🔐 Ottieni credenziali da variabili d'ambiente
DROPBOX_REFRESH_TOKEN = os.environ.get('DROPBOX_REFRESH_TOKEN')
DROPBOX_CLIENT_ID = os.environ.get('DROPBOX_CLIENT_ID')
DROPBOX_CLIENT_SECRET = os.environ.get('DROPBOX_CLIENT_SECRET')

# 🔄 Recupera un access token valido
def get_access_token():
    logging.info("🔄 Richiesta access token da Dropbox...")
    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': DROPBOX_REFRESH_TOKEN,
        'client_id': DROPBOX_CLIENT_ID,
        'client_secret': DROPBOX_CLIENT_SECRET,
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        access_token = response.json()['access_token']
        logging.info("✅ Access token ottenuto correttamente.")
        return access_token
    except Exception as e:
        logging.error("❌ Errore nel recupero del token Dropbox: %s", e)
        return None

# 📤 Carica un file su Dropbox
def upload_to_dropbox(file_stream, file_name):
    access_token = get_access_token()
    if not access_token:
        return False, "❌ Access token non disponibile."

    dropbox_path = f"/mtoXLSX/{file_name}.xlsx"
    upload_url = "https://content.dropboxapi.com/2/files/upload"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": str({
            "path": dropbox_path,
            "mode": "overwrite",
            "autorename": False,
            "mute": False,
            "strict_conflict": False
        }).replace("'", '"'),
        "Content-Type": "application/octet-stream",
    }

    try:
        logging.info(f"📁 Upload in corso su Dropbox: {dropbox_path}")
        response = requests.post(upload_url, headers=headers, data=file_stream.read())
        response.raise_for_status()
        logging.info("✅ File caricato correttamente su Dropbox.")
        return True, "✅ Upload completato"
    except Exception as e:
        logging.error("❌ Errore nell'upload su Dropbox: %s", e)
        return False, str(e)
