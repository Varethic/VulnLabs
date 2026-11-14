from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter(prefix="/labs/api-security", tags=["API Security"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

API_FLAG = "FLAG{bola_api_sensitive_field_exposure_5519}"

VULN_CODE = """@router.get("/api/v1/users/{user_id}")
def get_user_record(user_id: int):
    cursor.execute("SELECT * FROM api_users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return dict(row)
"""

FIX_CODE = """class UserPublicResponse(BaseModel):
    id: int
    username: str
    email: str

@router.get("/api/v1/users/{user_id}", response_model=UserPublicResponse)
def get_user_record(user_id: int):
    cursor.execute("SELECT id, username, email FROM api_users WHERE id = ?", (user_id,))
    return cursor.fetchone()
"""


@router.get("", response_class=HTMLResponse)
def api_view(request: Request, user_id: int = 1):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    user_data = dict(row) if row else None
    flag = user_data.get("secret_flag") if user_data and user_data.get("secret_flag") != "NONE" else None

    return templates.TemplateResponse(
        request=request,
        name="api.html",
        context={
            "user_id": user_id,
            "user_data": user_data,
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "api",
        },
    )


@router.get("/api/v1/users/{user_id}", response_class=JSONResponse)
def api_user_endpoint(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return JSONResponse(status_code=404, content={"error": "User record not found"})
