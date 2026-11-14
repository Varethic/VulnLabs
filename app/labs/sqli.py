import sqlite3
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.database import get_db

router = APIRouter(prefix="/labs/sqli", tags=["SQL Injection"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

AUTH_BYPASS_VULN_CODE = """@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    if user:
        return {"status": "authenticated", "user": user["username"]}
"""

AUTH_FIX_CODE = """@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    if user:
        return {"status": "authenticated", "user": user["username"]}
"""

UNION_VULN_CODE = """@router.get("/search")
def search_products(q: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    query = f"SELECT id, name, category, price, description FROM products WHERE name LIKE '%{q}%'"
    cursor.execute(query)
    return cursor.fetchall()
"""

UNION_FIX_CODE = """@router.get("/search")
def search_products(q: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT id, name, category, price, description FROM products WHERE name LIKE ? OR description LIKE ?"
    pattern = f"%{q}%"
    cursor.execute(query, (pattern, pattern))
    return cursor.fetchall()
"""


@router.get("", response_class=HTMLResponse)
def sqli_lab_view(request: Request, q: str = ""):
    search_results = []
    search_error = None
    executed_search_query = None

    if q != "":
        conn = get_db()
        cursor = conn.cursor()
        executed_search_query = f"SELECT id, name, category, price, description FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
        try:
            cursor.execute(executed_search_query)
            rows = cursor.fetchall()
            search_results = [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            search_error = str(e)
        finally:
            conn.close()

    return templates.TemplateResponse(
        request=request,
        name="sqli.html",
        context={
            "q": q,
            "search_results": search_results,
            "search_error": search_error,
            "executed_search_query": executed_search_query,
            "auth_code_snippet": AUTH_BYPASS_VULN_CODE,
            "auth_fix_code": AUTH_FIX_CODE,
            "union_code_snippet": UNION_VULN_CODE,
            "union_fix_code": UNION_FIX_CODE,
            "active_tab": "sqli",
        },
    )


@router.post("/login", response_class=HTMLResponse)
def sqli_login(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
):
    conn = get_db()
    cursor = conn.cursor()

    executed_query = f"SELECT id, username, role, secret_flag FROM users WHERE username = '{username}' AND password = '{password}'"
    login_result = None
    login_error = None
    flag = None

    try:
        cursor.execute(executed_query)
        user = cursor.fetchone()
        if user:
            user_dict = dict(user)
            if user_dict["role"] == "administrator" or user_dict["username"] == "admin":
                flag = "FLAG{sqli_auth_bypass_login_pwned_8192}"
                login_result = {
                    "success": True,
                    "message": f"Authenticated as administrator: {user_dict['username']}.",
                    "user": user_dict,
                    "flag": flag,
                }
            else:
                login_result = {
                    "success": True,
                    "message": f"Authenticated as user '{user_dict['username']}' ({user_dict['role']}). Administrator access required.",
                    "user": user_dict,
                    "flag": None,
                }
        else:
            login_result = {
                "success": False,
                "message": "Invalid username or password.",
            }
    except sqlite3.OperationalError as e:
        login_error = str(e)
    finally:
        conn.close()

    return templates.TemplateResponse(
        request=request,
        name="sqli.html",
        context={
            "login_result": login_result,
            "login_error": login_error,
            "executed_login_query": executed_query,
            "auth_code_snippet": AUTH_BYPASS_VULN_CODE,
            "auth_fix_code": AUTH_FIX_CODE,
            "union_code_snippet": UNION_VULN_CODE,
            "union_fix_code": UNION_FIX_CODE,
            "username_val": username,
            "active_tab": "sqli",
        },
    )
