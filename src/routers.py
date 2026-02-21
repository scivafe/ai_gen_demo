from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.quiz.router import router as quiz_router

all_routers: list[APIRouter] = [quiz_router, auth_router]
