from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db, reset_lab_environment
from app.flags import CHALLENGES, FLAG_MAP
from app.labs import sqli, xss, idor, cmdi, lfi, jwt_lab, ssrf, ssti, race

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Web Application Security Training Environment",
    description="Hands-on web security laboratory covering vulnerability analysis and secure implementation patterns.",
    version="1.0.0",
    lifespan=lifespan,
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(sqli.router)
app.include_router(xss.router)
app.include_router(idor.router)
app.include_router(cmdi.router)
app.include_router(lfi.router)
app.include_router(jwt_lab.router)
app.include_router(ssrf.router)
app.include_router(ssti.router)
app.include_router(race.router)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_solved_challenges(request: Request) -> set:
    cookie_val = request.cookies.get("solved_challenges", "")
    if not cookie_val:
        return set()
    return set(cid.strip() for cid in cookie_val.split(",") if cid.strip() in CHALLENGES)


def calculate_progress(solved_ids: set) -> dict:
    total_challenges = len(CHALLENGES)
    solved_count = len(solved_ids)
    percent = int((solved_count / total_challenges) * 100) if total_challenges > 0 else 0
    return {
        "total_challenges": total_challenges,
        "solved_count": solved_count,
        "percent": percent,
    }


@app.get("/", response_class=HTMLResponse)
def dashboard_view(
    request: Request,
    msg: Optional[str] = None,
    msg_type: Optional[str] = None,
):
    solved_set = get_solved_challenges(request)
    stats = calculate_progress(solved_set)

    challenges_list = []
    for cid, ch in CHALLENGES.items():
        item = dict(ch)
        item["is_solved"] = cid in solved_set
        challenges_list.append(item)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "challenges": challenges_list,
            "stats": stats,
            "solved_set": solved_set,
            "msg": msg,
            "msg_type": msg_type,
            "active_tab": "dashboard",
        },
    )


@app.post("/submit-flag")
async def submit_flag(
    request: Request,
    flag: str = Form(""),
):
    flag = flag.strip()
    is_json = "application/json" in request.headers.get("accept", "")
    solved_set = get_solved_challenges(request)

    if not flag:
        err_msg = "Please provide a flag string before submitting."
        if is_json:
            return JSONResponse(status_code=400, content={"success": False, "message": err_msg})
        return RedirectResponse(url=f"/?msg={err_msg}&msg_type=error", status_code=status.HTTP_303_SEE_OTHER)

    challenge_id = FLAG_MAP.get(flag)

    if not challenge_id:
        err_msg = f"Invalid flag submission: '{flag}'. Review your analysis and try again."
        if is_json:
            return JSONResponse(status_code=400, content={"success": False, "message": err_msg})
        base_referer = request.headers.get("referer", "/").split("?")[0]
        return RedirectResponse(
            url=f"{base_referer}?msg={err_msg}&msg_type=error",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    challenge = CHALLENGES[challenge_id]

    if challenge_id in solved_set:
        info_msg = f"Already Completed: You have verified '{challenge['title']}'."
        if is_json:
            return JSONResponse(content={"success": True, "already_solved": True, "message": info_msg})
        base_referer = request.headers.get("referer", "/").split("?")[0]
        return RedirectResponse(
            url=f"{base_referer}?msg={info_msg}&msg_type=info",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    solved_set.add(challenge_id)
    new_cookie_val = ",".join(solved_set)
    succ_msg = f"Verified: Challenge '{challenge['title']}' completed successfully."

    if is_json:
        response = JSONResponse(
            content={
                "success": True,
                "challenge": challenge["title"],
                "message": succ_msg,
            }
        )
        response.set_cookie(
            key="solved_challenges",
            value=new_cookie_val,
            max_age=31536000,
            httponly=False,
            samesite="lax",
        )
        return response

    base_referer = request.headers.get("referer", "/").split("?")[0]
    response = RedirectResponse(
        url=f"{base_referer}?msg={succ_msg}&msg_type=success",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        key="solved_challenges",
        value=new_cookie_val,
        max_age=31536000,
        httponly=False,
        samesite="lax",
    )
    return response


@app.post("/reset-progress")
def reset_progress(request: Request):
    referer = request.headers.get("referer", "/").split("?")[0]
    response = RedirectResponse(
        url=f"{referer}?msg=Lab progress reset.&msg_type=info",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie(key="solved_challenges")
    return response


@app.post("/reset-environment")
def reset_environment(request: Request):
    reset_lab_environment()
    referer = request.headers.get("referer", "/").split("?")[0]
    return RedirectResponse(
        url=f"{referer}?msg=Environment reset: Database state restored to defaults.&msg_type=success",
        status_code=status.HTTP_303_SEE_OTHER,
    )
