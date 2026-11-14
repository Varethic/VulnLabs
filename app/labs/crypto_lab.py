import time
import random
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/crypto", tags=["Cryptographic Failures"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

CRYPTO_FLAG = "FLAG{weak_prng_predictable_token_7734}"
RESET_STATE = {}

VULN_CODE = """@router.post("/request-reset")
def request_password_reset(email: str = Form(...)):
    current_time = int(time.time())
    random.seed(current_time)
    token = f"{random.randint(100000, 999999)}"
    send_reset_email(email, token)
    return {"status": "sent", "timestamp": current_time}
"""

FIX_CODE = """import secrets

@router.post("/request-reset")
def request_password_reset(email: str = Form(...)):
    token = secrets.token_urlsafe(32)
    send_reset_email(email, token)
    return {"status": "sent"}
"""


@router.get("", response_class=HTMLResponse)
def crypto_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="crypto.html",
        context={
            "token_info": None,
            "verification_result": None,
            "flag": None,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "crypto",
        },
    )


@router.post("/request-reset", response_class=HTMLResponse)
def request_reset(request: Request, email: str = Form("admin@academy.local")):
    t = int(time.time())
    random.seed(t)
    tok = str(random.randint(100000, 999999))
    RESET_STATE[email] = {"token": tok, "time": t}

    token_info = {
        "email": email,
        "seed_timestamp": t,
        "hint": "Token dispatched to administrative mailbox.",
    }

    return templates.TemplateResponse(
        request=request,
        name="crypto.html",
        context={
            "token_info": token_info,
            "verification_result": None,
            "flag": None,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "crypto",
        },
    )


@router.post("/verify-token", response_class=HTMLResponse)
def verify_token(request: Request, email: str = Form(""), token: str = Form("")):
    state = RESET_STATE.get(email.strip())
    flag = None
    verification_result = None

    if state and state["token"] == token.strip():
        flag = CRYPTO_FLAG
        verification_result = {
            "success": True,
            "message": "Token accepted: Cryptographic state compromised.",
        }
    else:
        verification_result = {
            "success": False,
            "message": "Invalid or expired token.",
        }

    return templates.TemplateResponse(
        request=request,
        name="crypto.html",
        context={
            "token_info": None,
            "verification_result": verification_result,
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "crypto",
        },
    )
