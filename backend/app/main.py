from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.utils.response import error_envelope
from app.routers import auth

app = FastAPI(title="AssetFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(code=exc.error_code, message=exc.message),
    )


app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "message": "AssetFlow API"
    }