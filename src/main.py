import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import anthropic
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from scalar_fastapi import get_scalar_api_reference

from src.auth.middleware import JWTAuthMiddleware
from src.database import Base, engine
from src.routers import all_routers

# Init GlitchTip/Sentry crash reporting in production
if os.getenv("ENVIRONMENT", "development") == "production":
    dsn = os.getenv("SENTRY_DSN")

    if dsn is None:
        logging.getLogger("uvicorn").warning(
            "SENTRY_DSN not set in production environment"
        )
    else:
        sentry_sdk.init(dsn)

openapi_title = "Gen AI Demo API"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Create tables if they don't exist yet
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=openapi_title,
    description="Gen AI Demo",
    version="0.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


# Expose Bearer auth in the OpenAPI schema for Scalar
def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # ty:ignore[invalid-assignment]

cors_env = os.getenv("CORS_ORIGINS")
origins = cors_env.split(";") if cors_env else ["*"]

app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JWTAuthMiddleware)  # ty:ignore[invalid-argument-type]

logger = logging.getLogger("uvicorn")


for router in all_routers:
    app.include_router(router)


# Serve Scalar docs only in development
if os.getenv("ENVIRONMENT", "production") == "development":

    @app.get("/docs", include_in_schema=False)
    async def scalar_html() -> HTMLResponse:
        return get_scalar_api_reference(
            title=openapi_title,
            openapi_url=app.openapi_url,
        )
