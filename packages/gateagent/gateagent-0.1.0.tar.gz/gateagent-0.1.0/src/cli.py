# gate/ext/cli.py

import uvicorn

def start():
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=5001,
        reload=False
    )
