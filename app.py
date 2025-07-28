import io
import logging
from dropbox_uploader import upload_to_dropbox, get_access_token

# Configurazione variabili (metti qui le tue credenziali)
REFRESH_TOKEN = "il_tuo_refresh_token"
CLIENT_ID = "il_tuo_client_id"
CLIENT_SECRET = "il_tuo_client_secret"

def handle_webhook(data):
    # Genera il file Excel in memoria (output)
    output = genera_excel(data)

    # Usa un nome fisso o con codice unico (qui esempio fisso)
    filename = "/mtoXLSX/fileMTO.xlsx"

    # Ottieni access token valido
    access_token = get_access_token(REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET)
    if not access_token:
        logging.error("Impossibile ottenere access token.")
        return False, "Access token fallito"

    # Upload su Dropbox
    file_stream = io.BytesIO(output)  # output dev’essere bytes, non stringa
    success, message = upload_to_dropbox(file_stream, filename, access_token)
    return success, message

def genera_excel(data):
    # Qui il tuo codice che crea il file XLSX in memoria e lo ritorna come bytes
    # ...
    pass
