import socket
import time
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

    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on port {PORT}...")

        while True:
            time.sleep(1.0)
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
        exit

