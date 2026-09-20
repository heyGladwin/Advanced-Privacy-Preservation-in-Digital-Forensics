from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.evidence import router as evidence_router
from app.routes.blockchain import router as blockchain_router
from app.routes.analysis_ai import router as analysis_router
from app.routes.fhe import router as fhe_router
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

app.include_router(
    auth_router,
    prefix="/api"
)

app.include_router(
    evidence_router,
    prefix="/api"
)
app.include_router(
    blockchain_router,
    prefix="/api"
)
app.include_router(
    analysis_router,
    prefix="/api"
)
app.include_router(
    fhe_router,
    prefix="/api"
)
@app.get("/")
def root():

    return {
        "message": "ForenCrypt API is running"
    }

