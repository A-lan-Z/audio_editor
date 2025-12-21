from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from backend.api.projects import router as projects_router
from backend.api.upload import router as upload_router
from backend.utils.errors import InvalidAudioFormat, ProjectNotFound, ValidationError
from backend.utils.logging_config import configure_logging
from backend.utils.request_limits import MaxBodySizeMiddleware
from backend.utils.storage import StorageError

app = FastAPI(title="TextAudio Edit API")

configure_logging()
logger = logging.getLogger("textaudio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(projects_router)
app.include_router(upload_router)
app.add_middleware(MaxBodySizeMiddleware)


def _error_response(
    *, status_code: int, error: str, detail: str, code: str
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "detail": detail, "code": code},
    )


@app.exception_handler(ProjectNotFound)
async def handle_project_not_found(_: Request, exc: ProjectNotFound) -> JSONResponse:
    return _error_response(
        status_code=404,
        error="Not Found",
        detail=str(exc),
        code="PROJECT_NOT_FOUND",
    )


@app.exception_handler(InvalidAudioFormat)
async def handle_invalid_audio_format(
    _: Request, exc: InvalidAudioFormat
) -> JSONResponse:
    return _error_response(
        status_code=400,
        error="Bad Request",
        detail=str(exc),
        code="INVALID_AUDIO_FORMAT",
    )


@app.exception_handler(ValidationError)
async def handle_validation_error(_: Request, exc: ValidationError) -> JSONResponse:
    return _error_response(
        status_code=400,
        error="Bad Request",
        detail=str(exc),
        code="VALIDATION_ERROR",
    )


@app.exception_handler(StorageError)
async def handle_storage_error(_: Request, exc: StorageError) -> JSONResponse:
    logger.exception("Storage error")
    return _error_response(
        status_code=500,
        error="Server Error",
        detail="Internal storage error",
        code="STORAGE_ERROR",
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {}
    msg = first.get("msg") or "Validation failed"
    return _error_response(
        status_code=422,
        error="Unprocessable Entity",
        detail=str(msg),
        code="REQUEST_VALIDATION_ERROR",
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(
    _: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        error="HTTP Error",
        detail=str(exc.detail),
        code="HTTP_EXCEPTION",
    )


@app.exception_handler(Exception)
async def handle_unhandled_exception(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return _error_response(
        status_code=500,
        error="Server Error",
        detail="Internal server error",
        code="INTERNAL_SERVER_ERROR",
    )
