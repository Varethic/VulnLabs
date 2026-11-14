import os
from pathlib import Path
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/lfi", tags=["Local File Inclusion"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

LFI_VULN_CODE = """@router.get("/download")
def download_file(file: str = Query(...)):
    if file.startswith("/") or (len(file) > 2 and file[1] == ":"):
        target_path = file
    else:
        target_path = os.path.join(DOCS_DIR, file)

    with open(target_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
"""

LFI_FIX_CODE = """import os
from pathlib import Path

SAFE_DOCS_DIR = Path("/app/app/docs").resolve()
ALLOWED_FILES = {"company_policy.txt", "system_status.txt", "changelog.txt"}

@router.get("/download")
def download_file(file: str = Query(...)):
    filename = os.path.basename(file)
    if filename not in ALLOWED_FILES:
        raise HTTPException(status_code=403, detail="File access not permitted")

    target_path = (SAFE_DOCS_DIR / filename).resolve()
    if not target_path.is_relative_to(SAFE_DOCS_DIR):
        raise HTTPException(status_code=403, detail="Path traversal attempt blocked")

    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()
"""


@router.get("", response_class=HTMLResponse)
def lfi_lab_view(request: Request, file: str = Query(None)):
    file_content = None
    file_error = None
    resolved_path_display = None

    default_files = []
    if DOCS_DIR.exists():
        default_files = [f.name for f in DOCS_DIR.iterdir() if f.is_file()]

    if file:
        file = file.strip()
        try:
            if file.startswith("/") or (len(file) > 2 and file[1] == ":"):
                target_path = Path(file)
            else:
                target_path = DOCS_DIR / file

            if not target_path.exists():
                alt_root = PROJECT_ROOT / file.lstrip("/\\")
                if alt_root.exists() and alt_root.is_file():
                    target_path = alt_root

            resolved_path_display = str(target_path)

            if target_path.exists() and target_path.is_file():
                with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                    file_content = f.read()
            else:
                file_error = f"Error: Target file '{file}' could not be located on the filesystem."
        except Exception as e:
            file_error = f"Filesystem access exception: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="lfi.html",
        context={
            "selected_file": file,
            "default_files": default_files,
            "file_content": file_content,
            "file_error": file_error,
            "resolved_path": resolved_path_display,
            "lfi_code_snippet": LFI_VULN_CODE,
            "lfi_fix_code": LFI_FIX_CODE,
            "active_tab": "lfi",
        },
    )


@router.get("/download")
def download_raw_file(file: str = Query(...)):
    file = file.strip()
    try:
        if file.startswith("/") or (len(file) > 2 and file[1] == ":"):
            target_path = Path(file)
        else:
            target_path = DOCS_DIR / file

        if not target_path.exists():
            alt_root = PROJECT_ROOT / file.lstrip("/\\")
            if alt_root.exists() and alt_root.is_file():
                target_path = alt_root

        if target_path.exists() and target_path.is_file():
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return PlainTextResponse(
                content=content,
                headers={"Content-Disposition": f'inline; filename="{target_path.name}"'},
            )
        else:
            return PlainTextResponse(f"File '{file}' not found.", status_code=404)
    except Exception as e:
        return PlainTextResponse(f"Server error: {str(e)}", status_code=500)
