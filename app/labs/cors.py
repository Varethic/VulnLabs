from pathlib import Path
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/cors", tags=["CORS Misconfiguration"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

CORS_FLAG = "FLAG{cors_arbitrary_origin_credential_leak_3391}"

VULN_CODE = """@router.get("/api/account-keys")
def get_account_keys(request: Request):
    origin = request.headers.get("origin", "*")
    response = JSONResponse(content={"account": "admin", "api_key": "AK_SEC_9941"})
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
"""

FIX_CODE = """TRUSTED_ORIGINS = {"https://academy.local", "https://trusted.internal"}

@router.get("/api/account-keys")
def get_account_keys(request: Request):
    origin = request.headers.get("origin", "")
    response = JSONResponse(content={"account": "admin", "api_key": "AK_SEC_9941"})
    if origin in TRUSTED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
"""


@router.get("", response_class=HTMLResponse)
def cors_view(request: Request, simulated_origin: str = "https://attacker-origin.local"):
    headers_returned = {
        "Access-Control-Allow-Origin": simulated_origin if simulated_origin else "None",
        "Access-Control-Allow-Credentials": "true",
        "Vary": "Origin",
    }
    flag = None
    if simulated_origin and "attacker" in simulated_origin or simulated_origin.startswith("http"):
        flag = CORS_FLAG

    return templates.TemplateResponse(
        request=request,
        name="cors.html",
        context={
            "simulated_origin": simulated_origin,
            "headers_returned": headers_returned,
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "cors",
        },
    )


@router.get("/api/account-keys", response_class=JSONResponse)
def account_keys_api(request: Request):
    origin = request.headers.get("origin", "*")
    payload = {
        "account": "executive_sec_officer",
        "environment": "enclave_production",
        "access_token": "tok_priv_889102",
        "secret_flag": CORS_FLAG,
    }
    response = JSONResponse(content=payload)
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Vary"] = "Origin"
    return response
