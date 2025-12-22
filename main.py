import socket
import asyncio
from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn


from listen import receive_text, HOST, PORT

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
ADDRESS = (HOST,PORT)


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket,address=ADDRESS):
#     await websocket.accept()
#     _, port = address
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind(address)
#         s.listen()
#         print(f"Listening on port {port}...")

#         while True:
#             await asyncio.sleep(1.0)
#             conn, addr = s.accept()
#             with conn:
#                 print(f"Connected by {addr}")
#                 while True:
#                     # result = unpickle_data(conn)
#                     result = receive_text(conn=conn) 
#                     if result is None:
#                         conn.close()
#                         break
#                     await websocket.send_text(result)

@app.get("/")
async def get_homepage(request: Request):
    return templates.TemplateResponse(request=request,context={},name="index.html")


@app.post("/")
async def post_line(request: Request):
    return JSONResponse(context={"request": request,"status": status.HTTP_200_OK})


if __name__ == "__main__":
    uvicorn.run(app,"localhost",8000)