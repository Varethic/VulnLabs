from pathlib import Path
from fastapi import APIRouter, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/headers", tags=["Header Spoofing"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

HEADER_FLAG = "FLAG{header_spoofing_client_ip_bypass_4102}"

VULN_CODE = """@router.get("/admin-panel")
def admin_panel(request: Request):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    if client_ip in ("127.0.0.1", "localhost", "::1"):
        return {"status": "authorized", "panel": "Access Granted"}
    raise HTTPException(status_code=403, detail="Remote access prohibited")
"""

FIX_CODE = """@router.get("/admin-panel")
def admin_panel(request: Request):
    real_ip = request.client.host
    if real_ip not in ("127.0.0.1", "::1"):
        raise HTTPException(status_code=403, detail="Access denied")
"""


@router.get("", response_class=HTMLResponse)
def headers_view(request: Request, simulated_ip: str = "192.168.1.105"):
    actual_ip = request.client.host if request.client else "127.0.0.1"
    eval_ip = simulated_ip.strip() if simulated_ip else actual_ip

    is_authorized = eval_ip in ("127.0.0.1", "localhost", "::1")
    flag = HEADER_FLAG if is_authorized else None

    return templates.TemplateResponse(
        request=request,
        name="headers.html",
        context={
            "eval_ip": eval_ip,
            "actual_ip": actual_ip,
            "is_authorized": is_authorized,
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "headers",
        },
    )


@router.get("/admin-panel", response_class=JSONResponse)
def admin_panel_api(request: Request):
    forwarded = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "127.0.0.1")
    if client_ip in ("127.0.0.1", "localhost", "::1"):
        return {
            "status": "AUTHORIZED_LOCAL_ADMIN",
            "evaluated_ip": client_ip,
            "flag": HEADER_FLAG,
        }
    return JSONResponse(
        status_code=403,
        content={"status": "FORBIDDEN", "detail": "Access restricted to local administrative interface (127.0.0.1).", "evaluated_ip": client_ip},
    )
