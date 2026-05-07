import os
from django.conf import settings
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


SCOPES = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly'
]

def get_credentials():
    token_path = os.path.join(settings.BASE_DIR, 'token.json')

    creds = None

    # Cargar token existente
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no es válido
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Renovando token automáticamente...")
            creds.refresh(Request())
        else:
            raise Exception("Debes generar el token manual una vez")

        # Guardar token actualizado
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds