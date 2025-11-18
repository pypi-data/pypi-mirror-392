# gate/ext/google_oauth.py

import os
import json
import requests
from urllib.parse import urlencode

GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5001/api/auth/google/callback"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

CRED_FILE = "google_creds.json"


def get_auth_url():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "scope": " ".join(SCOPES),
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def exchange_code_for_tokens(code: str):
    url = "https://oauth2.googleapis.com/token"

    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    r = requests.post(url, data=payload)
    r.raise_for_status()
    tokens = r.json()

    # save tokens to file
    with open(CRED_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return tokens


def load_tokens():
    if not os.path.exists(CRED_FILE):
        return None
    with open(CRED_FILE) as f:
        return json.load(f)
