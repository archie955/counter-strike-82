import logging

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from exceptions.app_exceptions import AppException
from logger.configuration import configure_logging
from logger.logging_middleware import LoggingMiddleware
from routers import users
from utils.config import settings

origins = settings.allowed_origins.split(",")

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(users.router)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception:
        return {"status": "unhealthy"}


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    logger.warning(
        "%s: %s",
        exc.__class__.__name__,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
def global_expression_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def root():
    return {"message": "home page"}
