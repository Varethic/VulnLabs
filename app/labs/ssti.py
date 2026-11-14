import jinja2
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/labs/ssti", tags=["SSTI"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

FLAG_SSTI = "FLAG{ssti_jinja2_template_rce_8812}"

SSTI_VULN_CODE = """@router.post("/render")
def render_badge(name: str = Form(...), title: str = Form(...)):
    template_str = f'''
    <div class="user-badge">
        <h3>Badge: {name}</h3>
        <p>Title: {title}</p>
    </div>
    '''
    rendered = jinja2.Environment().from_string(template_str).render()
    return {"rendered_badge": rendered}
"""

SSTI_FIX_CODE = """@router.post("/render")
def render_badge(name: str = Form(...), title: str = Form(...)):
    template_str = '''
    <div class="user-badge">
        <h3>Badge: {{ name }}</h3>
        <p>Title: {{ title }}</p>
    </div>
    '''
    env = jinja2.Environment(autoescape=True)
    rendered = env.from_string(template_str).render(name=name, title=title)
    return {"rendered_badge": rendered}
"""


@router.get("", response_class=HTMLResponse)
def ssti_lab_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="ssti.html",
        context={
            "name": "Alex",
            "title": "Security Analyst",
            "rendered_output": None,
            "ssti_error": None,
            "ssti_vuln_code": SSTI_VULN_CODE,
            "ssti_fix_code": SSTI_FIX_CODE,
            "active_tab": "ssti",
        },
    )


@router.post("/render", response_class=HTMLResponse)
def render_custom_badge(
    request: Request,
    name: str = Form("Alex"),
    title: str = Form("Security Analyst"),
):
    rendered_output = None
    ssti_error = None

    raw_template_string = f"""
    <div class="p-4 bg-black rounded-md border border-zinc-700 font-mono text-xs space-y-2">
        <div class="text-zinc-400">Recipient:</div>
        <div class="text-white text-sm font-bold">{name}</div>
        <div class="text-zinc-400 mt-2">Designation:</div>
        <div class="text-zinc-200">{title}</div>
    </div>
    """

    try:
        env = jinja2.Environment()
        env.globals["SYSTEM_FLAG"] = FLAG_SSTI
        env.globals["SECRET_TOKEN"] = FLAG_SSTI

        template = env.from_string(raw_template_string)
        rendered_output = template.render(flag=FLAG_SSTI)
    except Exception as e:
        ssti_error = f"Template rendering error: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="ssti.html",
        context={
            "name": name,
            "title": title,
            "rendered_output": rendered_output,
            "ssti_error": ssti_error,
            "ssti_vuln_code": SSTI_VULN_CODE,
            "ssti_fix_code": SSTI_FIX_CODE,
            "active_tab": "ssti",
        },
    )
