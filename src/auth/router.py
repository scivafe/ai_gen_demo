from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.auth.models.user import Token, UserCreate, UserResponse
from src.auth.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_username,
)
from src.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def signup(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing = get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    user = create_user(db, user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
def login(credentials: UserCreate, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def read_current_user(request: Request) -> UserResponse:
    return UserResponse.model_validate(request.state.user)
