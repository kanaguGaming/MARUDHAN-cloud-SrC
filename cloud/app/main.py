from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.router import api_router
from app.api.farmer_chat import farmer_router
from app.db.pathivu import connect_to_pathivu, close_pathivu_connection
import os

app = FastAPI(title="MARUDHAN OS - Cloud Backend", version="2.0", description="Centralized Cloud-Heavy AI Processing")

# Setup UI paths mapping to the existing cloud directory structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(BASE_DIR, "static")
templates_path = os.path.join(BASE_DIR, "templates")

# Ensure directories exist
os.makedirs(os.path.join(static_path, "css"), exist_ok=True)
os.makedirs(os.path.join(static_path, "js"), exist_ok=True)
os.makedirs(templates_path, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

app.include_router(api_router, prefix="/api/v1")
app.include_router(farmer_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    await connect_to_pathivu()

@app.on_event("shutdown")
async def shutdown_event():
    await close_pathivu_connection()

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the Digital Twin Dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status")
def read_root():
    return {"status": "MARUDHAN OS is running", "architecture": "Cloud-Heavy, Edge-Light"}


