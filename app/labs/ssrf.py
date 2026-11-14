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
FLAG_METADATA = "FLAG{ssrf_cloud_metadata_credential_leak_6631}"

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

SSRF_META_VULN_CODE = """@router.post("/check-metadata")
def check_metadata(meta_url: str = Form(...)):
    return httpx.get(meta_url, timeout=3.0).text
"""

SSRF_META_FIX_CODE = """import ipaddress
from urllib.parse import urlparse

@router.post("/check-metadata")
def check_metadata(meta_url: str = Form(...)):
    parsed = urlparse(meta_url)
    ip = socket.gethostbyname(parsed.hostname)
    ip_obj = ipaddress.ip_address(ip)
    if ip_obj.is_link_local or str(ip_obj) == "169.254.169.254":
        return {"error": "Link-local cloud metadata access forbidden"}
    return httpx.get(meta_url, timeout=3.0).text
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
            "meta_submitted_url": "http://169.254.169.254/latest/meta-data/",
            "meta_status": None,
            "meta_body": None,
            "meta_error": None,
            "ssrf_vuln_code": SSRF_VULN_CODE,
            "ssrf_fix_code": SSRF_FIX_CODE,
            "ssrf_meta_vuln_code": SSRF_META_VULN_CODE,
            "ssrf_meta_fix_code": SSRF_META_FIX_CODE,
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
    elif "169.254.169.254" in target_url:
        preview_status = 200
        cleaned = target_url.split("169.254.169.254")[-1].rstrip("/")
        if cleaned in ("", "/latest", "/latest/meta-data"):
            preview_body = "ami-id\nhostname\niam/\ninstance-id\nlocal-ipv4\npublic-keys"
        elif cleaned == "/latest/meta-data/iam":
            preview_body = "security-credentials/"
        elif cleaned == "/latest/meta-data/iam/security-credentials":
            preview_body = "ProductionAppRole"
        elif "ProductionAppRole" in cleaned or "security-credentials" in cleaned:
            preview_body = json.dumps(
                {
                    "Code": "Success",
                    "LastUpdated": "2026-11-14T08:00:00Z",
                    "Type": "AWS-HMAC",
                    "AccessKeyId": "ASIAV4R3TH1CEXAMPLE",
                    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "Token": FLAG_METADATA,
                    "Expiration": "2026-11-15T08:00:00Z",
                },
                indent=2,
            )
        else:
            preview_body = "ami-id\nhostname\niam/\ninstance-id\nlocal-ipv4"
    elif "internal-admin" in target_url:
        if "secret-flag" in target_url:
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
            preview_status = 200
            preview_body = json.dumps(
                {
                    "cluster": "internal-admin:9000",
                    "services": ["metrics", "healthz", "secret-flag"],
                    "status": "running",
                },
                indent=2,
            )
    else:
        try:
            with httpx.Client(timeout=4.0, follow_redirects=True) as client:
                res = client.get(target_url)
                preview_status = res.status_code
                preview_body = res.text
        except Exception as e:
            preview_error = f"Connection failed: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="ssrf.html",
        context={
            "submitted_url": target_url,
            "preview_status": preview_status,
            "preview_body": preview_body,
            "preview_error": preview_error,
            "meta_submitted_url": "http://169.254.169.254/latest/meta-data/",
            "meta_status": None,
            "meta_body": None,
            "meta_error": None,
            "ssrf_vuln_code": SSRF_VULN_CODE,
            "ssrf_fix_code": SSRF_FIX_CODE,
            "ssrf_meta_vuln_code": SSRF_META_VULN_CODE,
            "ssrf_meta_fix_code": SSRF_META_FIX_CODE,
            "active_tab": "ssrf",
        },
    )


@router.post("/check-metadata", response_class=HTMLResponse)
def check_metadata(request: Request, meta_url: str = Form("http://169.254.169.254/latest/meta-data/")):
    meta_url = meta_url.strip()
    meta_status = None
    meta_body = None
    meta_error = None

    if not meta_url:
        meta_error = "Please provide a metadata endpoint URL."
    elif "169.254.169.254" in meta_url:
        meta_status = 200
        cleaned = meta_url.split("169.254.169.254")[-1].rstrip("/")
        if cleaned in ("", "/latest", "/latest/meta-data"):
            meta_body = "ami-id\nhostname\niam/\ninstance-id\nlocal-ipv4\npublic-keys"
        elif cleaned == "/latest/meta-data/iam":
            meta_body = "security-credentials/"
        elif cleaned == "/latest/meta-data/iam/security-credentials":
            meta_body = "ProductionAppRole"
        elif "ProductionAppRole" in cleaned or "security-credentials" in cleaned:
            meta_body = json.dumps(
                {
                    "Code": "Success",
                    "LastUpdated": "2026-11-14T08:00:00Z",
                    "Type": "AWS-HMAC",
                    "AccessKeyId": "ASIAV4R3TH1CEXAMPLE",
                    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "Token": FLAG_METADATA,
                    "Expiration": "2026-11-15T08:00:00Z",
                },
                indent=2,
            )
        else:
            meta_body = "ami-id\nhostname\niam/\ninstance-id\nlocal-ipv4"
    else:
        meta_status = 403
        meta_error = "Target is not within cloud link-local metadata address space (169.254.169.254)."

    return templates.TemplateResponse(
        request=request,
        name="ssrf.html",
        context={
            "submitted_url": "http://example.com",
            "preview_status": None,
            "preview_body": None,
            "preview_error": None,
            "meta_submitted_url": meta_url,
            "meta_status": meta_status,
            "meta_body": meta_body,
            "meta_error": meta_error,
            "ssrf_vuln_code": SSRF_VULN_CODE,
            "ssrf_fix_code": SSRF_FIX_CODE,
            "ssrf_meta_vuln_code": SSRF_META_VULN_CODE,
            "ssrf_meta_fix_code": SSRF_META_FIX_CODE,
            "active_tab": "ssrf",
        },
    )
