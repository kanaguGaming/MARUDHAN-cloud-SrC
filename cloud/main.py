from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.endpoints import router
from db.database import connect_to_mongo, close_mongo_connection
import os

app = FastAPI(title="Marudhan Cloud API", description="Digital Twin & ARIVU Engine Backend")

# Ensure static dir exists before mounting to avoid startup errors
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
