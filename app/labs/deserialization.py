import base64
import pickle
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/deserialization", tags=["Insecure Deserialization"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

DESER_FLAG = "FLAG{insecure_pickle_deserialization_rce_5541}"

VULN_CODE = """@router.post("/load")
def load_user_session(session_data: str = Form(...)):
    raw_bytes = base64.b64decode(session_data)
    user_state = pickle.loads(raw_bytes)
    return {"status": "loaded", "state": str(user_state)}
"""

FIX_CODE = """import json

@router.post("/load")
def load_user_session(session_data: str = Form(...)):
    raw_str = base64.b64decode(session_data).decode()
    user_state = json.loads(raw_str)
    return {"status": "loaded", "state": user_state}
"""


@router.get("", response_class=HTMLResponse)
def deser_view(request: Request):
    default_dict = {"user": "analyst", "role": "student", "theme": "monochrome"}
    default_payload = base64.b64encode(pickle.dumps(default_dict)).decode()
    return templates.TemplateResponse(
        request=request,
        name="deserialization.html",
        context={
            "payload_input": default_payload,
            "deserialized_data": None,
            "error": None,
            "flag": None,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "deserialization",
        },
    )


@router.post("/load", response_class=HTMLResponse)
def load_session(request: Request, payload: str = Form("")):
    deserialized_data = None
    error = None
    flag = None
    try:
        raw_bytes = base64.b64decode(payload.strip())
        obj = pickle.loads(raw_bytes)
        deserialized_data = str(obj)
        if isinstance(obj, dict):
            if obj.get("role") == "admin" or obj.get("exploit"):
                flag = DESER_FLAG
        elif hasattr(obj, "__reduce__") or "rce" in str(type(obj)).lower() or "flag" in str(obj).lower() or type(obj).__name__ not in ("dict", "list", "str", "int", "bool"):
            flag = DESER_FLAG
    except Exception as e:
        error = str(e)

    return templates.TemplateResponse(
        request=request,
        name="deserialization.html",
        context={
            "payload_input": payload,
            "deserialized_data": deserialized_data,
            "error": error,
            "flag": flag,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "deserialization",
        },
    )
