from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

@app.post("/logs")
async def receive_log(
    message: str = Form(...),
    levelname: str = Form(...),
    logger: str = Form(...),
):
    """Receive logs from HTTPHandler and save to source-indexed files."""
    log_file = LOG_DIR / f"{logger}.log"
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{levelname}] {message}\n"

    with open(log_file, "a") as f:
        f.write(log_entry)

    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render dashboard with list of log files."""
    log_files = [f.name for f in LOG_DIR.glob("*.log")]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "log_files": log_files}
    )

@app.get("/logs/{filename}", response_class=HTMLResponse)
async def view_log(request: Request, filename: str):
    """Display contents of a log file."""
    log_file = LOG_DIR / filename
    if not log_file.exists():
        return {"error": "File not found"}

    with open(log_file, "r") as f:
        log_content = f.read()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "log_files": [f.name for f in LOG_DIR.glob("*.log")],
            "current_log": filename,
            "log_content": log_content,
        }
    )


@app.post("/debug")
async def debug(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    print(headers)
    print(body)
    return {
        "headers": headers,
        "body": body.decode("utf-8"),
        "form": await request.form(),
    }