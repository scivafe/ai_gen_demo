import json
from typing import cast

from anthropic import Anthropic
from anthropic.types import TextBlock

from src.quiz.models.quiz import QuizResponse

SYSTEM_PROMPT = """You are a quiz generator. Given a text, you must generate exactly 3 multiple-choice quiz questions based on its content.

Respond ONLY with a valid JSON object in this exact format, no other text:
{
  "quizzes": [
    {
      "question": "The question text",
      "a": {"text": "Option A", "correct": false},
      "b": {"text": "Option B", "correct": true},
      "c": {"text": "Option C", "correct": false},
      "d": {"text": "Option D", "correct": false}
    }
  ]
}

Rules:
- Generate exactly 3 questions
- Each question must have exactly 4 options (a, b, c, d)
- Exactly one option per question must have "correct": true
- All other options must have "correct": false"""


def create_quiz(text: str) -> QuizResponse:
    client = Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    data = json.loads(cast(TextBlock, message.content[0]).text)
    return QuizResponse(**data)
