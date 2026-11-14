import asyncio
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.database import get_db

router = APIRouter(prefix="/labs/race", tags=["Race Condition"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

FLAG_RACE = "FLAG{race_condition_toctou_balance_glitch_4011}"
FLAG_COST = 50.0
PROMO_CODE = "FREE10"

RACE_VULN_CODE = """@router.post("/redeem")
async def redeem_coupon(code: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT coupon_used FROM wallets WHERE user_id = 1")
    wallet = cursor.fetchone()

    if wallet["coupon_used"]:
        return {"error": "Coupon already used"}

    await asyncio.sleep(0.2)

    cursor.execute("UPDATE wallets SET balance = balance + 10.0, coupon_used = 1 WHERE user_id = 1")
    conn.commit()
    return {"status": "success"}
"""

RACE_FIX_CODE = """@router.post("/redeem")
async def redeem_coupon(code: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        \"\"\"
        UPDATE wallets
        SET balance = balance + 10.0, coupon_used = 1
        WHERE user_id = 1 AND coupon_used = 0
        \"\"\"
    )
    conn.commit()

    if cursor.rowcount == 0:
        return {"error": "Coupon already applied or invalid"}

    return {"status": "success"}
"""


def get_wallet():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, coupon_used, flag_purchased FROM wallets WHERE user_id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"balance": 10.0, "coupon_used": 0, "flag_purchased": 0}


@router.get("", response_class=HTMLResponse)
def race_lab_view(
    request: Request,
    message: str = None,
    msg_type: str = None,
):
    wallet = get_wallet()
    return templates.TemplateResponse(
        request=request,
        name="race.html",
        context={
            "wallet": wallet,
            "promo_code": PROMO_CODE,
            "flag_cost": FLAG_COST,
            "flag_value": FLAG_RACE,
            "action_message": message,
            "action_type": msg_type,
            "race_vuln_code": RACE_VULN_CODE,
            "race_fix_code": RACE_FIX_CODE,
            "active_tab": "race",
        },
    )


@router.post("/redeem")
async def redeem_coupon(
    request: Request,
    code: str = Form(""),
):
    code = code.strip().upper()
    is_json = "application/json" in request.headers.get("accept", "")

    if code != PROMO_CODE:
        err = f"Invalid code '{code}'."
        if is_json:
            return JSONResponse(status_code=400, content={"success": False, "message": err})
        return race_lab_view(request, message=err, msg_type="error")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT balance, coupon_used FROM wallets WHERE user_id = 1")
    row = cursor.fetchone()

    if not row:
        conn.close()
        err = "Account wallet not found."
        if is_json:
            return JSONResponse(status_code=404, content={"success": False, "message": err})
        return race_lab_view(request, message=err, msg_type="error")

    if row["coupon_used"] == 1:
        conn.close()
        err = "Code has already been redeemed."
        if is_json:
            return JSONResponse(status_code=400, content={"success": False, "message": err})
        return race_lab_view(request, message=err, msg_type="error")

    await asyncio.sleep(0.2)

    cursor.execute(
        "UPDATE wallets SET balance = balance + 10.0, coupon_used = 1 WHERE user_id = 1"
    )
    conn.commit()

    cursor.execute("SELECT balance FROM wallets WHERE user_id = 1")
    new_balance = cursor.fetchone()["balance"]
    conn.close()

    succ = f"Code redeemed. Balance: ${new_balance:.2f}"
    if is_json:
        return JSONResponse(content={"success": True, "balance": new_balance, "message": succ})
    return race_lab_view(request, message=succ, msg_type="success")


@router.post("/buy-flag", response_class=HTMLResponse)
def buy_flag(request: Request):
    wallet = get_wallet()
    if wallet["balance"] >= FLAG_COST:
        conn = get_db()
        cursor = conn.cursor()
        new_balance = wallet["balance"] - FLAG_COST
        cursor.execute(
            "UPDATE wallets SET balance = ?, flag_purchased = 1 WHERE user_id = 1",
            (new_balance,),
        )
        conn.commit()
        conn.close()
        msg = f"Completed: Flag unlocked: {FLAG_RACE}"
        return race_lab_view(request, message=msg, msg_type="success")
    else:
        err = f"Insufficient balance (${wallet['balance']:.2f} / ${FLAG_COST:.2f} required)."
        return race_lab_view(request, message=err, msg_type="error")


@router.post("/reset", response_class=HTMLResponse)
def reset_wallet(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE wallets SET balance = 10.0, coupon_used = 0, flag_purchased = 0 WHERE user_id = 1")
    conn.commit()
    conn.close()
    return race_lab_view(request, message="Wallet balance reset to $10.00.", msg_type="info")
