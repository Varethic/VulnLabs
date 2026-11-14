import os
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter(prefix="/labs/upload", tags=["File Upload"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

UPLOAD_FLAG = "FLAG{unrestricted_file_upload_stored_xss_8820}"
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

VULN_CODE = """@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    save_path = UPLOAD_DIR / filename
    with open(save_path, "wb") as f:
        f.write(await file.read())
    return {"status": "saved", "url": f"/static/uploads/{filename}"}
"""

FIX_CODE = """ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid extension")
    safe_name = f"{uuid.uuid4().hex}{ext}"
    with open(UPLOAD_DIR / safe_name, "wb") as f:
        f.write(await file.read())
"""


@router.get("", response_class=HTMLResponse)
def upload_view(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, original_name, content_type, uploaded_at FROM uploads ORDER BY id DESC")
    files = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "files": files,
            "message": None,
            "flag": None,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "upload",
        },
    )


@router.post("", response_class=HTMLResponse)
async def handle_upload(request: Request, file: UploadFile = File(...)):
    filename = file.filename
    raw_content = await file.read()
    save_path = UPLOAD_DIR / filename
    with open(save_path, "wb") as f:
        f.write(raw_content)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO uploads (filename, original_name, content_type) VALUES (?, ?, ?)",
        (filename, filename, file.content_type or "application/octet-stream"),
    )
    conn.commit()
    cursor.execute("SELECT id, filename, original_name, content_type, uploaded_at FROM uploads ORDER BY id DESC")
    files = [dict(r) for r in cursor.fetchall()]
    conn.close()

    flag = None
    ext = Path(filename).suffix.lower()
    content_str = raw_content.decode("utf-8", errors="ignore").lower()
    if ext in (".html", ".htm", ".svg", ".php", ".py", ".sh", ".jsp") or "<script" in content_str or "onerror=" in content_str:
        flag = UPLOAD_FLAG

    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "files": files,
            "message": f"File '{filename}' successfully saved to storage.",
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "upload",
        },
    )
