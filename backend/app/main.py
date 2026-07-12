from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.exceptions import AppException
from utils.response import error_envelope

from routers import auth, department, asset, category, allocation, transfer ,report


app = FastAPI(title="AssetFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before demo/prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(exc.error_code, exc.message, exc.detail),
    )


app.include_router(auth.router)
app.include_router(department.router)
app.include_router(asset.router)
app.include_router(category.router)
app.include_router(allocation.router)
app.include_router(transfer.router)
app.include_router(report.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}