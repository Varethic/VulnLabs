import sys
import subprocess
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/labs/cmdi", tags=["Command Injection"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

CMDI_VULN_CODE = """@router.post("/ping")
def run_ping(target: str = Form(...)):
    if sys.platform == "win32":
        cmd = f"ping -n 1 {target}"
    else:
        cmd = f"ping -c 1 {target}"

    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    return {"diagnostic_output": output.decode()}
"""

CMDI_FIX_CODE = """import ipaddress
import subprocess

@router.post("/ping")
def run_ping(target: str = Form(...)):
    try:
        ip = ipaddress.ip_address(target.strip())
        clean_ip = str(ip)
    except ValueError:
        return {"error": "Invalid IP address"}

    cmd = ["ping", "-c", "1", clean_ip]
    output = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
    return {"diagnostic_output": output.decode()}
"""


@router.get("", response_class=HTMLResponse)
def cmdi_lab_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cmdi.html",
        context={
            "target": "127.0.0.1",
            "output": None,
            "cmdi_code_snippet": CMDI_VULN_CODE,
            "cmdi_fix_code": CMDI_FIX_CODE,
            "active_tab": "cmdi",
        },
    )


@router.post("/ping", response_class=HTMLResponse)
def execute_ping(request: Request, target: str = Form("127.0.0.1")):
    target = target.strip()
    terminal_output = ""
    executed_command = ""

    if target:
        if sys.platform == "win32":
            executed_command = f"ping -n 1 {target}"
        else:
            executed_command = f"ping -c 1 {target}"

        try:
            raw_output = subprocess.check_output(
                executed_command,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=6,
            )
            terminal_output = raw_output.decode("utf-8", errors="replace")
        except subprocess.CalledProcessError as e:
            terminal_output = e.output.decode("utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            terminal_output = "Diagnostic command timed out."
        except Exception as e:
            terminal_output = f"Execution error: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="cmdi.html",
        context={
            "target": target,
            "output": terminal_output,
            "executed_command": executed_command,
            "cmdi_code_snippet": CMDI_VULN_CODE,
            "cmdi_fix_code": CMDI_FIX_CODE,
            "active_tab": "cmdi",
        },
    )
