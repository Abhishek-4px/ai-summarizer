import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.routes import router

app = FastAPI(title="AI Text Summarizer")

app.include_router(router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
