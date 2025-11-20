# gate/ext/models.py

from typing import Optional, TypedDict

class TrackEvent(TypedDict):
    event: str             # "start" or "end"
    agent: str
    action: str
    timestamp: float       # UNIX epoch
    success: Optional[bool]
    

class StoredEvent(TypedDict):
    id: int
    event: str
    agent: str
    action: str
    timestamp: float
    success: Optional[bool]
    created_at: str
