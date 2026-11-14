import json
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter(prefix="/labs/mass-assignment", tags=["Mass Assignment"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

MASS_FLAG = "FLAG{mass_assignment_privilege_escalation_1289}"

VULN_CODE = """@router.post("/profile")
async def update_profile(request: Request):
    data = await request.json()
    for field, val in data.items():
        cursor.execute(f"UPDATE profile_users SET {field} = ? WHERE id = 1", (val,))
    conn.commit()
"""

FIX_CODE = """@router.post("/profile")
def update_profile(username: str = Form(...), bio: str = Form(...)):
    ALLOWED_FIELDS = {"username", "bio"}
    cursor.execute("UPDATE profile_users SET username = ?, bio = ? WHERE id = 1", (username, bio))
    conn.commit()
"""


@router.get("", response_class=HTMLResponse)
def mass_view(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, bio FROM profile_users WHERE id = 1")
    user = dict(cursor.fetchone())
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="mass_assignment.html",
        context={
            "user": user,
            "message": None,
            "flag": None,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "mass-assignment",
        },
    )


@router.post("/profile", response_class=HTMLResponse)
async def update_profile(request: Request):
    conn = get_db()
    cursor = conn.cursor()

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    for field, val in data.items():
        if field in ("username", "email", "role", "bio"):
            cursor.execute(f"UPDATE profile_users SET {field} = ? WHERE id = 1", (str(val),))

    conn.commit()
    cursor.execute("SELECT id, username, email, role, bio FROM profile_users WHERE id = 1")
    user = dict(cursor.fetchone())
    conn.close()

    flag = None
    if user.get("role") in ("admin", "administrator", "root"):
        flag = MASS_FLAG

    return templates.TemplateResponse(
        request=request,
        name="mass_assignment.html",
        context={
            "user": user,
            "message": "User profile attributes committed successfully.",
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "mass-assignment",
        },
    )
