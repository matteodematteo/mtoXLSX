import dropbox
import requests
import os
import sys

# Legge le variabili d'ambiente definite su Render
APP_KEY = os.getenv("DROPBOX_CLIENT_ID")
APP_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_FOLDER = "/mtoXLSX"

def get_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def upload_file(local_path):
    file_name = os.path.basename(local_path)
    dropbox_path = f"{DROPBOX_FOLDER}/{file_name}"

    token = get_access_token()
    dbx = dropbox.Dropbox(token)

    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

    print(f"✅ File caricato su Dropbox: {dropbox_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Specifica il file .xlsx da caricare.")
        sys.exit(1)

    local_file = sys.argv[1]
    if not os.path.exists(local_file):
        print(f"❌ File non trovato: {local_file}")
        sys.exit(1)

    upload_file(local_file)
