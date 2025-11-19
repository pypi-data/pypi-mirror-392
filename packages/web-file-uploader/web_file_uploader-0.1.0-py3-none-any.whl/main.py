from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
from pathlib import Path

app = FastAPI(title="Web File Uploader", description="A simple file uploader using FastAPI")

# 創建上傳目錄
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Web File Uploader API", "docs": "/docs"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上傳單一檔案
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # 檢查檔案類型（可選）
    allowed_extensions = {'.txt', '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.docx', '.doc', '.ppt', '.pptx'}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    # 儲存檔案
    file_path = UPLOAD_DIR / file.filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return JSONResponse(
        status_code=200,
        content={
            "message": "File uploaded successfully",
            "filename": file.filename,
            "size": file_path.stat().st_size,
            "path": str(file_path),
            "download_url": f"/download/{file.filename}"
        }
    )

@app.get("/files")
def list_files():
    """
    列出已上傳的檔案
    """
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime
            })

    return {"files": files}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    下載指定檔案
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.delete("/files/{filename}")
def delete_file(filename: str):
    """
    刪除指定檔案
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
