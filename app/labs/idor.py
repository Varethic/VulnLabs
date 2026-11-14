import sqlite3
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.database import get_db

router = APIRouter(prefix="/labs/idor", tags=["Insecure Direct Object References"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

SIMULATED_SESSION = {
    "user_id": 2,
    "username": "alice",
    "full_name": "Alice Cooper",
    "role": "analyst",
}

IDOR_VULN_CODE = """@router.get("/receipt/{receipt_id}")
def get_receipt(request: Request, receipt_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM receipts WHERE id = ?", (receipt_id,))
    receipt = cursor.fetchone()
    return templates.TemplateResponse("receipt.html", {"receipt": receipt})
"""

IDOR_FIX_CODE = """@router.get("/receipt/{receipt_id}")
def get_receipt(request: Request, receipt_id: int):
    current_user_id = request.session.get("user_id")
    is_admin = request.session.get("role") == "administrator"

    conn = get_db()
    cursor = conn.cursor()
    if is_admin:
        cursor.execute("SELECT * FROM receipts WHERE id = ?", (receipt_id,))
    else:
        cursor.execute(
            "SELECT * FROM receipts WHERE id = ? AND user_id = ?",
            (receipt_id, current_user_id)
        )

    receipt = cursor.fetchone()
    if not receipt:
        raise HTTPException(status_code=403, detail="Forbidden")
    return templates.TemplateResponse("receipt.html", {"receipt": receipt})
"""


@router.get("", response_class=HTMLResponse)
def idor_lab_view(request: Request, receipt_id: int = Query(None)):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, amount FROM receipts WHERE user_id = ? ORDER BY id ASC",
        (SIMULATED_SESSION["user_id"],),
    )
    user_receipts = [dict(row) for row in cursor.fetchall()]

    selected_receipt = None
    not_found = False

    if receipt_id is not None:
        cursor.execute("SELECT * FROM receipts WHERE id = ?", (receipt_id,))
        row = cursor.fetchone()
        if row:
            selected_receipt = dict(row)
        else:
            not_found = True

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="idor.html",
        context={
            "current_user": SIMULATED_SESSION,
            "user_receipts": user_receipts,
            "selected_receipt": selected_receipt,
            "requested_id": receipt_id,
            "not_found": not_found,
            "idor_code_snippet": IDOR_VULN_CODE,
            "idor_fix_code": IDOR_FIX_CODE,
            "active_tab": "idor",
        },
    )


@router.get("/receipt/{receipt_id}", response_class=HTMLResponse)
def view_receipt_by_path(request: Request, receipt_id: int):
    return idor_lab_view(request, receipt_id=receipt_id)


@router.get("/api/receipt/{receipt_id}", response_class=JSONResponse)
def get_receipt_json(receipt_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM receipts WHERE id = ?", (receipt_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return JSONResponse(status_code=404, content={"error": f"Receipt #{receipt_id} not found."})

    receipt_data = dict(row)
    return JSONResponse(content={"status": "success", "receipt": receipt_data})
