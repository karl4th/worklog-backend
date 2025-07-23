import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.worklog import get_routes
import os

app = FastAPI(
    title="WorkLog - система управление задачами",
    version="2.1.0",
    description="Новая версия на новым движке. FastAPI",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://ortalyk.worklog.kz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

get_routes(app)

# Custom handler for file downloads
@app.get("/files/{file_path:path}")
async def download_file(file_path: str):
    file_location = f"uploads/{file_path}"
    if os.path.exists(file_location):
        return FileResponse(
            path=file_location,
            filename=file_path,
            media_type="application/octet-stream"
        )
    return {"error": "File not found"}

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)