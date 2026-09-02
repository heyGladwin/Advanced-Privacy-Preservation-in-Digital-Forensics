from fastapi import FastAPI

from app.routes.health import router as health_router


app = FastAPI(
    title="ForenCrypt API",
    description=(
        "Privacy-Preserving Digital Forensics "
        "Using AI, FHE and Hybrid Blockchain"
    ),
    version="1.0.0"
)


app.include_router(
    health_router,
    prefix="/api"
)


@app.get("/")
def root():

    return {
        "message": "ForenCrypt API is running"
    }