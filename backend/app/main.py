
# backend/app/main.py
import shutil
import tempfile
import os
from pathlib import Path
from zipfile import ZipFile
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.analyzer import analyze_project
import uvicorn

app = FastAPI(title="Project Inspector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://project-inspector-frontend.proudfield-b0f3558f.eastus.azurecontainerapps.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# StaticFiles mount — only needed for Option A (file-on-disk approach).
# Commented out because SVGs are now returned as data URIs (Option B in analyzer.py).
# Re-enable if switching back to file-based delivery.
# STATIC_DIR = Path("/app/static")
# STATIC_DIR.mkdir(parents=True, exist_ok=True)
# app.mount("/static", StaticFiles(directory="/app/static"), name="static")

MAX_ZIP_SIZE = 200 * 1024 * 1024  # 200 MB


@app.get("/health")
async def health_check():
    """Health check endpoint for Azure Container Apps readiness probes."""
    return {"status": "ok"}

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file")

    # read into temp file (stream to avoid memory blow)
    temp_zip_fd, temp_zip_path = tempfile.mkstemp(suffix=".zip")
    with os.fdopen(temp_zip_fd, "wb") as tmp:
        content = await file.read()
        if len(content) > MAX_ZIP_SIZE:
            raise HTTPException(status_code=413, detail="ZIP too large")
        tmp.write(content)

    # create temp dir for extraction
    extract_dir = Path(tempfile.mkdtemp(prefix="project_inspect_"))
    try:
        with ZipFile(temp_zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # Run analysis
        report = analyze_project(extract_dir)

        return JSONResponse(content=report)
    finally:
        # cleanup zip (but keep extracted results until process done)
        os.remove(temp_zip_path)
        # NOTE: analyzer may write files in extract_dir; depending on approach, clean here or after client downloads
        shutil.rmtree(extract_dir, ignore_errors=True)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
