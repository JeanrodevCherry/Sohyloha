from __future__ import annotations
import socket
import time
import asyncio
from fastapi import FastAPI, WebSocket, Request, Response, websockets
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

HOST = "127.0.0.1"
PORT = 5050

def receive_text(conn:socket):
    if not conn:
        return
    buffer = ""
    while "\n" not in buffer:
        data = conn.recv(1024).decode("utf-8")
        if not data:
            return buffer
        buffer += data
    return buffer.strip("\n")


def listenSocket(address: tuple):
    _, port = address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(address)
            s.listen()
            print(f"Listening on port {port}...")

            while True:
                time.sleep(0.5)
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        # result = unpickle_data(conn)
                        result = receive_text(conn=conn)
                        if result is None:
                            conn.close()
                            break
                        print(result)
        except KeyboardInterrupt as ke:
            print(f"{repr(ke)}")
            return
app = FastAPI()
templates = Jinja2Templates(directory="templates")
ADDRESS = (HOST,PORT)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,address=ADDRESS):
    await websocket.accept()
    _, port = address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(address)
        s.listen()
        print(f"Listening on port {port}...")
        while True:
            await asyncio.sleep(1.0)
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    # result = unpickle_data(conn)
                    result = receive_text(conn=conn) 
                    if result is None:
                        conn.close()
                        break
                    if websocket.client_state == websockets.WebSocketState.CONNECTED:
                        await websocket.send_text(result)
@app.get("/")
async def get_homepage(request: Request):
    return templates.TemplateResponse(request=request,context={},name="index.html")
