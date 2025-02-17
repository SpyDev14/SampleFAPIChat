from typing import List
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def send_personal_msg(self, msg: str, websocket: WebSocket):
        await websocket.send_text(msg)

    async def broadcast(self, msg: str, websocket: WebSocket):
        await websocket.send_text(msg)
        for connection in self.connections:
            if connection == websocket:
                continue
            await connection.send_text(msg)

# START

app = FastAPI()
pagesMan = Jinja2Templates(directory="pages")
connectionMan = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return pagesMan.TemplateResponse("index.html", {"request": request})

@app.websocket("connections/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await connectionMan.connect(websocket)
    try:
        while True:
            data = websocket.receive_text()
            await connectionMan.send_personal_msg(f"Хз1: {data}", websocket)

    except WebSocketDisconnect:
        connectionMan.disconnect(websocket)
        connectionMan.broadcast(f"Пользователь #{client_id} ливнул")