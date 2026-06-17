import os

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]


def get_credentials():
    token_path = os.path.join(settings.BASE_DIR, "token.json")
    credentials_path = os.path.join(
        settings.BASE_DIR,
        "credentials.json"
    )

    creds = None


    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(
            token_path,
            SCOPES
        )


    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())

            with open(token_path, "w") as token:
                token.write(creds.to_json())

            print("Token renovado correctamente")

        except Exception:
            creds = None


    if not creds:

        if not os.path.exists(credentials_path):
            raise Exception(
                "No existe credentials.json"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,
            SCOPES
        )

        creds = flow.run_local_server(
            port=8080,
            prompt="consent",
            access_type="offline"
        )

        with open(token_path, "w") as token:
            token.write(creds.to_json())

        print("Token generado correctamente")

    return creds