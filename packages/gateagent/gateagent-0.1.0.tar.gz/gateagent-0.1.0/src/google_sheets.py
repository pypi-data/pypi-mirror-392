# gate/ext/google_sheets.py
import time
import json
import requests
from typing import Optional

from google_oauth import load_tokens, exchange_code_for_tokens, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, CRED_FILE

TOKEN_URL = "https://oauth2.googleapis.com/token"
SHEETS_API_BASE = "https://sheets.googleapis.com/v4"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"


def _save_tokens(tokens: dict):
    # add timestamp of when tokens saved
    tokens["_saved_at"] = int(time.time())
    with open(CRED_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


def refresh_access_token(tokens: dict) -> dict:
    """Use refresh_token to get a new access_token. Returns updated tokens (and saves them)."""
    if not tokens or "refresh_token" not in tokens:
        raise ValueError("No refresh_token available")
    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token",
    }
    r = requests.post(TOKEN_URL, data=payload, timeout=10)
    r.raise_for_status()
    new = r.json()
    # merge refresh_token back if Google didn't return it
    if "refresh_token" not in new:
        new["refresh_token"] = tokens["refresh_token"]
    # preserve previous saved_at if any; new saved_at will be updated in _save_tokens
    _save_tokens(new)
    return new


def _get_valid_tokens():
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("No Google tokens saved. Authorize first.")
    # naive expiry check — if saved_at + expires_in < now -> refresh
    saved_at = tokens.get("_saved_at", 0)
    expires_in = tokens.get("expires_in")
    if expires_in and (saved_at + int(expires_in) - 60) < int(time.time()):
        tokens = refresh_access_token(tokens)
    return tokens


def _authorized_headers():
    tokens = _get_valid_tokens()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def list_drive_spreadsheets(page_size: int = 50):
    """List user drive files that are Google Sheets."""
    headers = _authorized_headers()
    params = {
        "q": "mimeType='application/vnd.google-apps.spreadsheet'",
        "pageSize": page_size,
        "fields": "files(id,name,modifiedTime),nextPageToken"
    }
    r = requests.get(f"{DRIVE_API_BASE}/files", headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def get_spreadsheet(spreadsheet_id: str):
    headers = _authorized_headers()
    r = requests.get(f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def read_values(spreadsheet_id: str, range_a1: str):
    headers = _authorized_headers()
    r = requests.get(f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def append_values(spreadsheet_id: str, range_a1: str, values: list, value_input_option: str = "RAW"):
    headers = _authorized_headers()
    params = {"valueInputOption": value_input_option}
    body = {"values": values}
    r = requests.post(f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}:append",
                      headers=headers, params=params, json=body, timeout=10)
    r.raise_for_status()
    return r.json()


def update_values(spreadsheet_id: str, range_a1: str, values: list, value_input_option: str = "RAW"):
    headers = _authorized_headers()
    body = {"values": values}
    params = {"valueInputOption": value_input_option}
    r = requests.put(f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}",
                     headers=headers, params=params, json=body, timeout=10)
    r.raise_for_status()
    return r.json()


def clear_values(spreadsheet_id: str, range_a1: str):
    headers = _authorized_headers()
    r = requests.post(f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}:clear",
                      headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()
