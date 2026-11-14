from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Internal Admin Microservice", docs_url=None, redoc_url=None)

INTERNAL_SSRF_FLAG = "FLAG{ssrf_internal_pivot_pwned_9941}"


@app.get("/")
def index():
    return {
        "service": "Internal Infrastructure Control Node",
        "status": "ONLINE",
        "network": "lab-net (Isolated Bridge)",
        "security_warning": "Restricted network segment. Public exposure prohibited.",
    }


@app.get("/secret-flag")
def get_secret_flag():
    return JSONResponse(
        content={
            "status": "AUTHORIZED_INTERNAL_ACCESS",
            "flag": INTERNAL_SSRF_FLAG,
            "description": "High-value SSRF internal pivot flag captured from isolated microservice.",
            "authorized_cluster": "internal-admin:9000",
        }
    )


@app.get("/system-status")
def system_status():
    return {
        "node": "prod-admin-01",
        "cluster_health": "OPTIMAL",
        "endpoints": ["/secret-flag", "/system-status"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
