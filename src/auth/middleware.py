from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.auth.services.auth import ALGORITHM, SECRET_KEY, get_user_by_username
from src.database import SessionLocal

PUBLIC_PATHS = {"/auth/signup", "/auth/login", "/openapi.json"}
PUBLIC_PREFIXES = ("/docs",)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        session_factory: sessionmaker[Session] = SessionLocal,
    ) -> None:
        super().__init__(app)
        self.session_factory = session_factory

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.removeprefix("Bearer ")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str | None = payload.get("sub")
            if username is None:
                raise JWTError("Missing sub claim")
        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        db = self.session_factory()
        try:
            user = get_user_by_username(db, username)
        finally:
            db.close()

        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "User not found"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user = user
        return await call_next(request)
