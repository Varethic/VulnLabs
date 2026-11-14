import json
import httpx
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/labs/ssrf", tags=["SSRF"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

FLAG_SSRF = "FLAG{ssrf_internal_pivot_pwned_9941}"

SSRF_VULN_CODE = """@router.post("/check-url")
def check_url(target_url: str = Form(...)):
    client = httpx.Client(timeout=5.0)
    response = client.get(target_url)
    return {"status": response.status_code, "body": response.text}
"""

SSRF_FIX_CODE = """import ipaddress
import socket
from urllib.parse import urlparse

@router.post("/check-url")
def check_url(target_url: str = Form(...)):
    parsed = urlparse(target_url)
    if parsed.scheme not in ("http", "https"):
        return {"error": "Invalid protocol"}

    try:
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
    except Exception:
        return {"error": "Resolution failure"}

    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
        return {"error": "Internal network destination forbidden"}

    response = httpx.get(target_url, timeout=3.0, follow_redirects=False)
    return {"status": response.status_code, "body": response.text[:1000]}
"""


@router.get("", response_class=HTMLResponse)
def ssrf_lab_view(request: Request, url: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="ssrf.html",
        context={
            "submitted_url": url or "http://example.com",
            "preview_status": None,
            "preview_body": None,
            "preview_error": None,
            "ssrf_vuln_code": SSRF_VULN_CODE,
            "ssrf_fix_code": SSRF_FIX_CODE,
            "active_tab": "ssrf",
        },
    )


@router.post("/check-url", response_class=HTMLResponse)
def check_url(request: Request, target_url: str = Form("http://example.com")):
    target_url = target_url.strip()
    preview_status = None
    preview_body = None
    preview_error = None

    if not target_url:
        preview_error = "Please provide an endpoint URL."
    else:
        try:
            with httpx.Client(timeout=4.0, follow_redirects=True) as client:
                res = client.get(target_url)
                preview_status = res.status_code
                preview_body = res.text
        except Exception as e:
            if "internal-admin" in target_url and "secret-flag" in target_url:
                preview_status = 200
                preview_body = json.dumps(
                    {
                        "status": "AUTHORIZED_INTERNAL_ACCESS",
                        "flag": FLAG_SSRF,
                        "description": "Internal cluster secret retrieved.",
                        "cluster": "internal-admin:9000",
                    },
                    indent=2,
                )
            else:
                preview_error = f"Connection failed: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="ssrf.html",
        context={
            "submitted_url": target_url,
            "preview_status": preview_status,
            "preview_body": preview_body,
            "preview_error": preview_error,
            "ssrf_vuln_code": SSRF_VULN_CODE,
            "ssrf_fix_code": SSRF_FIX_CODE,
            "active_tab": "ssrf",
        },
    )
