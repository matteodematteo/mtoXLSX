import json  # AGGIUNGI in cima al file
import os
import requests
import logging
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DROPBOX_CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")


def get_access_token():
    logger.info("🔐 Requesting Dropbox access token...")

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
        logger.info("✅ Access token obtained.")
    else:
        logger.error(f"❌ Failed to get access token: {response.text}")
        response.raise_for_status()

    return response.json()["access_token"]


def upload_to_dropbox(file_path, dropbox_path):
    logger.info(f"⬆️ Uploading to Dropbox: {dropbox_path}")

    access_token = get_access_token()

    with open(file_path, "rb") as f:
        data = f.read()

    headers = {
        "Authorization": f"Bearer {access_token}",
"Dropbox-API-Arg": json.dumps({
    "path": dropbox_path,
    "mode": "overwrite",
    "autorename": True,
    "mute": False,
    "strict_conflict": False
}),

        "Content-Type": "application/octet-stream"
    }

    upload_url = "https://content.dropboxapi.com/2/files/upload"
    res = requests.post(upload_url, headers=headers, data=data)

    if res.ok:
        logger.info(f"✅ Upload successful: {dropbox_path}")
    else:
        logger.error(f"❌ Upload failed: {res.text}")
        res.raise_for_status()

    return res.json()
