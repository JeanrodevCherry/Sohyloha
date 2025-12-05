from __future__ import annotations
import asyncio
import websockets
import socket
from functools  import partial
from listen import receive_text, HOST, PORT


async def proxy_socket(websocket, path, address):
    _, port = address # initial address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(address)
            s.listen()
            print(f"Listening on port {port}...")

            while True:
                # time.sleep(1.0)
                asyncio.sleep(1.0)
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        result = receive_text(conn=conn)
                        if result is None:
                            conn.close()
                            break
                        await websocket.send(result)
        except KeyboardInterrupt as ke:
            print(f"{repr(ke)}")
            return

handler = partial(proxy_socket,address=(HOST,PORT))

async def wrapped_handler(websocket,path):
    await handler(websocket,path)

async def main():
    async with websockets.serve(wrapped_handler, "0.0.0.0", 8000):
        print("WebSocket server running on ws://0.0.0.0:8000")
        await asyncio.Future()  # Run forever


if __name__=="__main__":
    asyncio.run(main())