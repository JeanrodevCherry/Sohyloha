from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
from threading import Lock
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log_lock = Lock()  # Thread-safe file writes
MAX_LOG_SIZE = 100 * 1024 * 1024  # 100MB per file


def get_log_filepath(device_name: str) -> Path:
    """Return the log file path for today (e.g., /logs/192.168.0.100/2024-02-20.log)."""
    today = datetime.now().strftime("%Y-%m-%d")
    device_dir = Path(LOG_DIR) / device_name
    device_dir.mkdir(exist_ok=True)
    return device_dir / f"{today}.log"

def rotate_log_if_needed(log_file: Path) -> None:
    """Rotate log if it exceeds MAX_LOG_SIZE."""
    if log_file.exists() and log_file.stat().st_size > MAX_LOG_SIZE:
        # Rename to .1, .2, etc. (like logrotate)
        for i in range(99, 0, -1):
            old = log_file.with_suffix(f".{i.zfill(3)}")
            new = log_file.with_suffix(f".{(i+1).zfill(3)}")
            if old.exists():
                old.rename(new)
        log_file.rename(log_file.with_suffix(".001"))


# @app.post("/logs")
# async def receive_log(
#     message: str = Form(...),
#     levelname: str = Form(...),
#     logger: str = Form(...),
# ):
#     """Receive logs from HTTPHandler and save to source-indexed files."""
#     log_file = LOG_DIR / f"{logger}.log"
#     timestamp = datetime.now().isoformat()
#     log_entry = f"[{timestamp}] [{levelname}] {message}\n"

#     with open(log_file, "a") as f:
#         f.write(log_entry)

#     return {"status": "ok"}

# @app.get("/", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     """Render dashboard with list of log files."""
#     log_files = [f.name for f in LOG_DIR.glob("*.log")]
#     return templates.TemplateResponse(
#         "index.html",
#         {"request": request, "log_files": log_files}
#     )

# @app.get("/logs/{filename}", response_class=HTMLResponse)
# async def view_log(request: Request, filename: str):
#     """Display contents of a log file."""
#     log_file = LOG_DIR / filename
#     if not log_file.exists():
#         return {"error": "File not found"}

#     with open(log_file, "r") as f:
#         log_content = f.read()

#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "log_files": [f.name for f in LOG_DIR.glob("*.log")],
#             "current_log": filename,
#             "log_content": log_content,
#         }
#     )


@app.post("/debug")
async def debug(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    device_name = request.client.host
    log_file = get_log_filepath(device_name)
    body_decoded = await request.form()
    client_ip = request.client.host
    log_level = body_decoded.get("levelname")
    message_ = body_decoded.get("message")
    timestamp_ = body_decoded.get("asctime")
    msg_ = f"[{log_level}]\t{timestamp_}\t{message_}"
    print(msg_)

    return JSONResponse(
        status_code=200,
        content={"status": "ok", "client_ip": client_ip, "log_file": str(log_file)},
    )

@app.post("/logs")
async def get_logs(request: Request):
    body = await request.body()
    device_name = request.client.host
    log_file = get_log_filepath(device_name)
    body_decoded = await request.form()
    log_level = body_decoded.get("levelname")
    message_ = body_decoded.get("message")
    timestamp_ = body_decoded.get("asctime")
    
    # msg_ = await request.form()
    # Rotate log if too large
    with log_lock:
        rotate_log_if_needed(log_file)

        # Append log entry (format: timestamp | level | message)
        # timestamp = datetime.now().isoformat()
        # log_entry = f"{timestamp} | {levelname.upper()} | {msg}\n"
        log_entry = f"[{log_level}]\t{timestamp_}\t{message_}\n"
        with open(log_file, "a") as f:
            f.write(log_entry)

    return JSONResponse(
        status_code=200,
        content={"status": "ok", "device": device_name, "log_file": str(log_file)},
    )