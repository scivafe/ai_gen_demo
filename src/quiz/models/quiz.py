from pydantic import BaseModel


class QuizRequest(BaseModel):
    text: str


class Option(BaseModel):
    text: str
    correct: bool


class Quiz(BaseModel):
    question: str
    a: Option
    b: Option
    c: Option
    d: Option


class QuizResponse(BaseModel):
    quizzes: list[Quiz]
