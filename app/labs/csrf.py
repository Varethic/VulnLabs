from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter(prefix="/labs/csrf", tags=["Cross-Site Request Forgery"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

CSRF_FLAG = "FLAG{csrf_state_changing_action_pwned_4431}"

VULN_CODE = """@router.post("/change-email")
def change_email(request: Request, email: str = Form(...)):
    session = request.cookies.get("csrf_session")
    if session == "victim_authorized_session":
        cursor.execute("UPDATE csrf_accounts SET email = ? WHERE id = 1", (email,))
        return {"status": "email_updated", "email": email}
"""

FIX_CODE = """@router.post("/change-email")
def change_email(request: Request, email: str = Form(...), csrf_token: str = Form(...)):
    if not verify_csrf_token(request, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    cursor.execute("UPDATE csrf_accounts SET email = ? WHERE id = 1", (email,))
"""


@router.get("", response_class=HTMLResponse)
def csrf_view(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, balance FROM csrf_accounts WHERE id = 1")
    account = dict(cursor.fetchone())
    conn.close()

    resp = templates.TemplateResponse(
        request=request,
        name="csrf.html",
        context={
            "account": account,
            "message": None,
            "flag": None,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "csrf",
        },
    )
    if "csrf_session" not in request.cookies:
        resp.set_cookie(key="csrf_session", value="victim_authorized_session", httponly=False, samesite="none", secure=False)
    return resp


@router.post("/change-email", response_class=HTMLResponse)
def change_email(request: Request, email: str = Form("")):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE csrf_accounts SET email = ? WHERE id = 1", (email.strip(),))
    conn.commit()

    cursor.execute("SELECT id, username, email, balance FROM csrf_accounts WHERE id = 1")
    account = dict(cursor.fetchone())
    conn.close()

    flag = None
    if "@" in email and email != "victim@company.local":
        flag = CSRF_FLAG

    return templates.TemplateResponse(
        request=request,
        name="csrf.html",
        context={
            "account": account,
            "message": f"Account email updated to: {email}",
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "csrf",
        },
    )


@router.post("/reset", response_class=HTMLResponse)
def reset_account(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE csrf_accounts SET email = 'victim@company.local' WHERE id = 1")
    conn.commit()
    conn.close()
    return csrf_view(request)
