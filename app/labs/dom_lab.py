from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/dom-xss", tags=["DOM XSS"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

DOM_FLAG = "FLAG{dom_xss_execution_sink_untrusted_source_9918}"

VULN_CODE = """<script>
  const params = new URLSearchParams(window.location.search);
  const nickname = params.get('nickname') || window.location.hash.substring(1);
  if (nickname) {
    document.getElementById('greeting').innerHTML = "Welcome, " + nickname;
  }
</script>
"""

FIX_CODE = """<script>
  const params = new URLSearchParams(window.location.search);
  const nickname = params.get('nickname') || window.location.hash.substring(1);
  if (nickname) {
    document.getElementById('greeting').textContent = "Welcome, " + nickname;
  }
</script>
"""


@router.get("", response_class=HTMLResponse)
def dom_view(request: Request, nickname: str = ""):
    flag = DOM_FLAG if ("<img" in nickname.lower() or "<script" in nickname.lower() or "onerror" in nickname.lower()) else None
    return templates.TemplateResponse(
        request=request,
        name="dom.html",
        context={
            "nickname": nickname,
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "dom-xss",
        },
    )
