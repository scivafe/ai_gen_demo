from unittest.mock import patch

from fastapi.testclient import TestClient

from src.quiz.models.quiz import QuizResponse

MOCK_RESPONSE = {
    "quizzes": [
        {
            "question": "What is Python?",
            "a": {"text": "A snake", "correct": False},
            "b": {"text": "A programming language", "correct": True},
            "c": {"text": "A car", "correct": False},
            "d": {"text": "A planet", "correct": False},
        },
        {
            "question": "What is 2+2?",
            "a": {"text": "3", "correct": False},
            "b": {"text": "4", "correct": True},
            "c": {"text": "5", "correct": False},
            "d": {"text": "6", "correct": False},
        },
        {
            "question": "What is HTTP?",
            "a": {"text": "A protocol", "correct": True},
            "b": {"text": "A language", "correct": False},
            "c": {"text": "A database", "correct": False},
            "d": {"text": "An OS", "correct": False},
        },
    ]
}


@patch("src.quiz.router.create_quiz")
def test_generate_quiz(
    mock_create_quiz, client: TestClient, auth_headers: dict[str, str]
) -> None:
    mock_create_quiz.return_value = QuizResponse.model_validate(MOCK_RESPONSE)

    resp = client.post(
        "/quiz/", json={"text": "Some text about Python"}, headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["quizzes"]) == 3
    assert data["quizzes"][0]["question"] == "What is Python?"


@patch("src.quiz.router.create_quiz")
def test_generate_quiz_empty_text(
    mock_create_quiz, client: TestClient, auth_headers: dict[str, str]
) -> None:
    mock_create_quiz.return_value = QuizResponse.model_validate(MOCK_RESPONSE)
    resp = client.post("/quiz/", json={"text": ""}, headers=auth_headers)
    assert resp.status_code == 200


def test_generate_quiz_no_token(client: TestClient) -> None:
    resp = client.post("/quiz/", json={"text": "hello"})
    assert resp.status_code == 401


def test_generate_quiz_missing_body(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.post("/quiz/", headers=auth_headers)
    assert resp.status_code == 422
