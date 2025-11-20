# gate/ext/server.py

from fastapi import FastAPI
from routes import router

app = FastAPI(title="Revert Gateway", version="0.1.0")

# single router import
app.include_router(router, prefix="/api")
