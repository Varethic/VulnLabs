from pathlib import Path
from urllib.parse import urlparse
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/redirect", tags=["Open Redirect"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

REDIRECT_FLAG = "FLAG{open_redirect_phishing_vector_6021}"

VULN_CODE = """@router.get("/go")
def redirect_to(url: str = ""):
    if url.startswith("/") or "academy.local" in url:
        return RedirectResponse(url=url)
    return RedirectResponse(url="/")
"""

FIX_CODE = """ALLOWED_HOSTS = {"academy.local", "127.0.0.1", "localhost"}

@router.get("/go")
def redirect_to(url: str = ""):
    parsed = urlparse(url)
    if not parsed.netloc or parsed.netloc in ALLOWED_HOSTS:
        return RedirectResponse(url=url)
    raise HTTPException(status_code=400, detail="Disallowed target destination")
"""


@router.get("", response_class=HTMLResponse)
def redirect_view(request: Request, url: str = ""):
    intercepted = None
    flag = None
    if url:
        parsed = urlparse(url)
        is_external = bool(parsed.netloc and parsed.netloc not in ("127.0.0.1", "localhost", "127.0.0.1:8000"))
        if is_external or url.startswith("//") or "evil.com" in url or "attacker.com" in url:
            flag = REDIRECT_FLAG
            intercepted = {
                "target": url,
                "domain": parsed.netloc or url,
                "status": "EXTERNAL_REDIRECTION_ALLOWED",
            }
        else:
            intercepted = {
                "target": url,
                "domain": parsed.netloc or "Local Origin",
                "status": "LOCAL_PATH_FORWARDED",
            }

    return templates.TemplateResponse(
        request=request,
        name="redirect.html",
        context={
            "url_input": url,
            "intercepted": intercepted,
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "redirect",
        },
    )


@router.get("/go")
def redirect_endpoint(url: str = "/"):
    parsed = urlparse(url)
    if url.startswith("/") or "academy.local" in url or bool(parsed.netloc):
        return RedirectResponse(url=f"/labs/redirect?url={url}")
    return RedirectResponse(url="/labs/redirect")
