import os
import requests

DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")

def get_access_token():
    token_url = "https://api.dropbox.com/oauth2/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN,
        "client_id": DROPBOX_CLIENT_ID,
        "client_secret": DROPBOX_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def upload_to_dropbox(file_stream, dropbox_path):
    access_token = get_access_token()
    if not access_token:
        return False, "Failed to get Dropbox access token"

    upload_url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": f'{{"path": "{dropbox_path}", "mode": "add", "autorename": true}}',
        "Content-Type": "application/octet-stream"
    }

    response = requests.post(upload_url, headers=headers, data=file_stream.read())
    if response.status_code == 200:
        return True, "Upload successful"
    return False, response.text
