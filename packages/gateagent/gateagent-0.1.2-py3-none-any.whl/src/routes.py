# gate/ext/routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from models import TrackEvent, StoredEvent
from db import insert_event, list_events
from google_oauth import get_auth_url, exchange_code_for_tokens, load_tokens

router = APIRouter()

# ------------------------------
# Healthcheck
# ------------------------------

@router.get("/healthcheck")
def healthcheck():
    return {"ok": True}

# ------------------------------
# Track Events
# ------------------------------

@router.post("/track")
def track_event(event: TrackEvent):
    insert_event(event)
    return {"ok": True}


# ------------------------------
# Fetch Events
# ------------------------------

@router.get("/events")
def get_events(limit: int = 200):
    rows = list_events(limit)

    result: list[StoredEvent] = []
    for r in rows:
        id_, event, agent, action, timestamp, success, created_at = r
        result.append(StoredEvent(
            id=id_,
            event=event,
            agent=agent,
            action=action,
            timestamp=timestamp,
            success=bool(success) if success is not None else None,
            created_at=created_at,
        ))

    return result


# ------------------------------
# Google OAuth
# ------------------------------

@router.get("/auth/google/url")
def google_auth_url():
    return {"auth_url": get_auth_url()}


# @router.get("/auth/google/callback")
# def google_auth_callback(code: str):
#     try:
#         tokens = exchange_code_for_tokens(code)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     return {"success": True, "tokens": tokens}

@router.get("/auth/google/callback")
def google_auth_callback(code: str):
    try:
        exchange_code_for_tokens(code)
    except Exception as e:
        # redirect to error page
        return RedirectResponse("/?auth_error=1")

    # redirect to UI dashboard
    return RedirectResponse("/?auth_success=1")

@router.get("/auth/google/status")
def google_auth_status():
    tokens = load_tokens()
    return {"authorized": bool(tokens)}
