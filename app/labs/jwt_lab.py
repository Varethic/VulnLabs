import jwt
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/labs/jwt", tags=["JWT Attacks"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

JWT_SECRET = "secret123"
FLAG_JWT = "FLAG{jwt_broken_verification_admin_3389}"

JWT_VULN_CODE = """@router.post("/admin-vault")
def access_admin_vault(token: str = Form(...)):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        if payload.get("role") == "admin":
            return {"status": "success", "flag": "..."}
        return {"status": "denied"}
    except Exception as e:
        return {"error": str(e)}
"""

JWT_FIX_CODE = """@router.post("/admin-vault")
def access_admin_vault(token: str = Form(...)):
    try:
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_signature": True}
        )
        if payload.get("role") == "admin":
            return {"status": "success", "flag": "..."}
        return {"status": "denied"}
    except jwt.PyJWTError as e:
        return {"error": str(e)}
"""


@router.get("", response_class=HTMLResponse)
def jwt_lab_view(request: Request, token: str = ""):
    guest_token = jwt.encode({"sub": "guest", "role": "user"}, JWT_SECRET, algorithm="HS256")
    return templates.TemplateResponse(
        request=request,
        name="jwt.html",
        context={
            "default_guest_token": guest_token,
            "submitted_token": token or guest_token,
            "vault_result": None,
            "vault_error": None,
            "jwt_vuln_code": JWT_VULN_CODE,
            "jwt_fix_code": JWT_FIX_CODE,
            "active_tab": "jwt",
        },
    )


@router.post("/login-guest", response_class=HTMLResponse)
def login_guest(request: Request):
    guest_token = jwt.encode({"sub": "guest", "role": "user"}, JWT_SECRET, algorithm="HS256")
    return jwt_lab_view(request, token=guest_token)


@router.post("/admin-vault", response_class=HTMLResponse)
def access_admin_vault(request: Request, token: str = Form("")):
    token = token.strip()
    guest_token = jwt.encode({"sub": "guest", "role": "user"}, JWT_SECRET, algorithm="HS256")
    vault_result = None
    vault_error = None

    if not token:
        vault_error = "Please supply a JWT token string."
    else:
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=["HS256", "none", "HS384", "HS512"],
            )

            user_role = payload.get("role")
            subject = payload.get("sub", "unknown")

            if user_role == "admin":
                vault_result = {
                    "success": True,
                    "message": f"Authorization verified for administrator account: {subject}.",
                    "payload": payload,
                    "flag": FLAG_JWT,
                }
            else:
                vault_result = {
                    "success": False,
                    "message": f"Access Denied: Subject '{subject}' has role '{user_role}'. Administrator role required.",
                    "payload": payload,
                    "flag": None,
                }
        except Exception as e:
            vault_error = f"Token parsing error: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="jwt.html",
        context={
            "default_guest_token": guest_token,
            "submitted_token": token,
            "vault_result": vault_result,
            "vault_error": vault_error,
            "jwt_vuln_code": JWT_VULN_CODE,
            "jwt_fix_code": JWT_FIX_CODE,
            "active_tab": "jwt",
        },
    )
