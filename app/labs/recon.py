from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/labs/recon", tags=["Reconnaissance"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

FLAG_RECON = "FLAG{recon_hidden_robots_path_disclosure_1982}"

RECON_VULN_CODE = """User-agent: *
Disallow: /restricted-archive/
Disallow: /labs/recon?view=secret-archive
"""

RECON_FIX_CODE = """@app.get("/restricted-archive/")
def restricted_archive(user: User = Depends(get_current_admin_user)):
    return {"archive": "confidential_data"}
"""


@router.get("", response_class=HTMLResponse)
def recon_lab_view(request: Request, view: str = ""):
    discovered_archive = False
    flag_content = None

    if view in ("secret-archive", "audit"):
        discovered_archive = True
        flag_content = FLAG_RECON

    return templates.TemplateResponse(
        request=request,
        name="recon.html",
        context={
            "probed_path": "",
            "probe_result": None,
            "discovered_archive": discovered_archive,
            "flag_content": flag_content,
            "recon_vuln_code": RECON_VULN_CODE,
            "recon_fix_code": RECON_FIX_CODE,
            "active_tab": "recon",
        },
    )


@router.post("/probe", response_class=HTMLResponse)
def probe_path(request: Request, path: str = Form("")):
    path = path.strip()
    discovered_archive = False
    flag_content = None
    probe_result = None

    normalized = path.lower()
    if "robots.txt" in normalized:
        probe_result = "User-agent: *\nDisallow: /admin\nDisallow: /restricted-archive/\nDisallow: /labs/recon?view=secret-archive\nDisallow: /internal-metrics/"
    elif "security.txt" in normalized:
        probe_result = "Contact: security-audit@cyber.lab\nExpires: 2027-12-31T23:59:59.000Z\nDisclose-Path: /labs/recon?view=secret-archive"
    elif "restricted-archive" in normalized or "secret-archive" in normalized:
        discovered_archive = True
        flag_content = FLAG_RECON
        probe_result = f"CONFIDENTIAL ARCHIVE CONTAINER DISCLOSED\nAccess Point: {path}\nPayload: {FLAG_RECON}"
    elif normalized in ("/admin", "/internal-metrics"):
        probe_result = "403 Forbidden: Endpoint restricted to authorized intranet callers."
    else:
        probe_result = f"404 Not Found: Path '{path}' does not resolve to an active endpoint."

    return templates.TemplateResponse(
        request=request,
        name="recon.html",
        context={
            "probed_path": path,
            "probe_result": probe_result,
            "discovered_archive": discovered_archive,
            "flag_content": flag_content,
            "recon_vuln_code": RECON_VULN_CODE,
            "recon_fix_code": RECON_FIX_CODE,
            "active_tab": "recon",
        },
    )
