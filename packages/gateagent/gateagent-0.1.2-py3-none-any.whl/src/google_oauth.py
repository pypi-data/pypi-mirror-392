# gate/ext/google_oauth.py

import os
import json
import time
import requests
from urllib.parse import urlencode

# load dotenv
from dotenv import load_dotenv
load_dotenv()

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

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

# --------------------------
# AUTO REFRESH LOGIC
# --------------------------

def refresh_access_token(tokens: dict):
    """Use refresh_token to get a new access_token"""
    if "refresh_token" not in tokens:
        raise RuntimeError("No refresh_token found. User must reauthorize.")

    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token",
    }
    r = requests.post("https://oauth2.googleapis.com/token", data=payload)
    r.raise_for_status()

    new_tokens = r.json()
    # Keep old refresh_token if Google does not send a new one
    if "refresh_token" not in new_tokens:
        new_tokens["refresh_token"] = tokens["refresh_token"]

    save_tokens(new_tokens)
    return new_tokens


def get_valid_tokens() -> dict:
    """Return tokens, refreshing access_token if expired"""
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("Google not authorized")

    saved_at = tokens.get("_saved_at", 0)
    expires_in = tokens.get("expires_in", 0)

    # Refresh 60 seconds before expiration
    if time.time() > saved_at + expires_in - 60:
        return refresh_access_token(tokens)

    return tokens


# --------------------------
# AUTH HEADERS FOR API CALLS
# --------------------------

def get_auth_headers():
    tokens = get_valid_tokens()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# --------------------------
# TOKEN FILE HELPERS
# --------------------------

def load_tokens():
    """Load stored tokens from google_creds.json"""
    if not os.path.exists(CRED_FILE):
        return None
    with open(CRED_FILE, "r") as f:
        return json.load(f)


def save_tokens(tokens: dict):
    """Save tokens with saved_at timestamp"""
    tokens["_saved_at"] = int(time.time())
    with open(CRED_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
