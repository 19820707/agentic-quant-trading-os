from fastapi import FastAPI

SERVICE_NAME = "reporting-engine"

app = FastAPI(title=SERVICE_NAME)


@app.get("/health")
def health() -> dict[str, object]:
    return {"service": SERVICE_NAME, "status": "ok", "external_calls": False}


@app.get("/ready")
def ready() -> dict[str, object]:
    return {"service": SERVICE_NAME, "ready": True, "trading_logic": False}

