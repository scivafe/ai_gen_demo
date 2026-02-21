from fastapi import APIRouter

from src.quiz.models.quiz import QuizRequest, QuizResponse
from src.quiz.services.quiz import create_quiz

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/")
def generate_quiz(req: QuizRequest) -> QuizResponse:
    return create_quiz(req.text)
