import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter(prefix="/labs/xss", tags=["Cross-Site Scripting"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

FLAG_BOT_XSS = "FLAG{xss_stole_admin_cookie}"

REFLECTED_VULN_CODE = """@router.get("/reflected")
def search(request: Request, query: str = ""):
    return templates.TemplateResponse(request=request, name="xss.html", context={"query": query})

<div class="search-output">
    Search query: {{ query | safe }}
</div>
"""

REFLECTED_FIX_CODE = """<div class="search-output">
    Search query: {{ query }}
</div>

response.set_cookie(
    key="session_token",
    value="...",
    httponly=True,
    secure=True,
    samesite="Strict"
)
"""

STORED_VULN_CODE = """@router.post("/guestbook")
def add_comment(author: str = Form(...), comment: str = Form(...)):
    cursor.execute("INSERT INTO guestbook (author, comment) VALUES (?, ?)", (author, comment))

<div class="comment-body">{{ entry.comment | safe }}</div>
"""

STORED_FIX_CODE = """import nh3

@router.post("/guestbook")
def add_comment(author: str = Form(...), comment: str = Form(...)):
    clean_comment = nh3.clean(comment, tags={"b", "i", "u", "p"})
    cursor.execute("INSERT INTO guestbook (author, comment) VALUES (?, ?)", (author, clean_comment))

<div class="comment-body">{{ entry.comment }}</div>
"""


async def run_playwright_admin_bot(target_url: str):
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
            context = await browser.new_context()
            await context.add_cookies([
                {
                    "name": "admin_session",
                    "value": FLAG_BOT_XSS,
                    "domain": "127.0.0.1",
                    "path": "/",
                    "httpOnly": False,
                    "secure": False,
                }
            ])
            page = await context.new_page()
            await page.goto(target_url, timeout=10000, wait_until="load")
            await page.wait_for_timeout(3000)
            await browser.close()
    except Exception as e:
        print(f"[!] Admin Bot Error: {e}")


@router.get("", response_class=HTMLResponse)
def xss_lab_view(request: Request, q: str = "", bot_status: str = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, comment, created_at FROM guestbook ORDER BY id DESC")
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()

    response = templates.TemplateResponse(
        request=request,
        name="xss.html",
        context={
            "q": q,
            "comments": comments,
            "bot_status": bot_status,
            "reflected_code_snippet": REFLECTED_VULN_CODE,
            "reflected_fix_code": REFLECTED_FIX_CODE,
            "stored_code_snippet": STORED_VULN_CODE,
            "stored_fix_code": STORED_FIX_CODE,
            "active_tab": "xss",
        },
    )

    if "session_token" not in request.cookies:
        response.set_cookie(
            key="session_token",
            value="FLAG{r3fl3ct3d_xss_c00k13_st0l3n_4421}",
            httponly=False,
            samesite="lax",
        )

    return response


@router.post("/guestbook", response_class=HTMLResponse)
def add_guestbook_comment(
    request: Request,
    author: str = Form("Anonymous"),
    comment: str = Form(""),
):
    if comment.strip():
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO guestbook (author, comment, created_at) VALUES (?, ?, ?)",
            (author.strip() or "Anonymous", comment, now),
        )
        conn.commit()
        conn.close()

    return xss_lab_view(request, bot_status="Comment submitted to guestbook.")


@router.post("/report", response_class=HTMLResponse)
async def report_to_admin(request: Request, background_tasks: BackgroundTasks):
    bot_target_url = "http://127.0.0.1:8000/labs/xss"
    background_tasks.add_task(run_playwright_admin_bot, bot_target_url)

    msg = "Report received. Automated administrator browser reviewing the guestbook (cookie: admin_session)."
    return xss_lab_view(request, bot_status=msg)


@router.post("/guestbook/reset", response_class=HTMLResponse)
def reset_guestbook(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM guestbook")
    cursor.execute(
        "INSERT INTO guestbook (author, comment, created_at) VALUES (?, ?, ?)",
        (
            "Security Officer",
            "Internal discussion board. Please post questions responsibly.",
            "2026-11-10 09:30:00",
        ),
    )
    cursor.execute(
        "INSERT INTO guestbook (author, comment, created_at) VALUES (?, ?, ?)",
        (
            "DevOps Engineer",
            "System maintenance scheduled for this Saturday at 02:00 UTC.",
            "2026-11-12 14:15:00",
        ),
    )
    conn.commit()
    conn.close()

    return xss_lab_view(request, bot_status="Guestbook reset to default entries.")
