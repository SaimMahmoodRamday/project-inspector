
# backend/app/main.py
import shutil
import tempfile
import os
from pathlib import Path
from zipfile import ZipFile
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.analyzer import analyze_project
import uvicorn
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Project Inspector")

STATIC_DIR = Path("/app/static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)  # ensures folder exists

# Serve call graph SVGs and any other static assets
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

MAX_ZIP_SIZE = 200 * 1024 * 1024  # 200 MB, adjust as needed

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

        # Optionally write report to disk and return a link or contents
        return JSONResponse(content=report)
    finally:
        # cleanup zip (but keep extracted results until process done)
        os.remove(temp_zip_path)
        # NOTE: analyzer may write files in extract_dir; depending on approach, clean here or after client downloads
        shutil.rmtree(extract_dir, ignore_errors=True)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
