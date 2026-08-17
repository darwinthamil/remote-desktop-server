import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, PlainTextResponse

app = FastAPI()

# ---------------------------------------------------------------------------
# Auth
#
# Set AUTH_TOKEN as an environment variable on Render (Dashboard -> your
# service -> Environment). Anyone connecting (laptop agent, browser client)
# must supply this token or they get rejected. Without this, anyone who
# finds your URL could view/control your machine.
# ---------------------------------------------------------------------------
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")

laptop_ws: WebSocket | None = None
browser_clients: set[WebSocket] = set()


def token_ok(token: str | None) -> bool:
    if not AUTH_TOKEN:
        # If no token configured, refuse everything rather than silently
        # running with no auth at all.
        return False
    return token == AUTH_TOKEN


@app.websocket("/laptop")
async def laptop_endpoint(ws: WebSocket, token: str = Query(default=None)):
    global laptop_ws
    if not token_ok(token):
        await ws.close(code=4401)
        return
    await ws.accept()
    laptop_ws = ws
    print("Laptop agent connected")
    try:
        while True:
            data = await ws.receive_bytes()
            disconnected = set()
            for client in browser_clients:
                try:
                    await client.send_bytes(data)
                except Exception:
                    disconnected.add(client)
            browser_clients.difference_update(disconnected)
    except WebSocketDisconnect:
        print("Laptop agent disconnected")
        laptop_ws = None


@app.websocket("/browser")
async def browser_endpoint(ws: WebSocket, token: str = Query(default=None)):
    if not token_ok(token):
        await ws.close(code=4401)
        return
    await ws.accept()
    browser_clients.add(ws)
    print(f"Browser client connected. Total: {len(browser_clients)}")
    try:
        while True:
            msg = await ws.receive_text()
            if laptop_ws:
                try:
                    await laptop_ws.send_text(msg)
                except Exception:
                    pass
    except WebSocketDisconnect:
        browser_clients.discard(ws)
        print(f"Browser client disconnected. Total: {len(browser_clients)}")


@app.get("/")
async def get_ui():
    with open(os.path.join(os.path.dirname(__file__), "static", "index.html")) as f:
        return HTMLResponse(f.read())


@app.get("/healthz")
async def health():
    return PlainTextResponse("ok")
