from pydantic import BaseModel
from typing import Dict, List

class QuizRequest(BaseModel):
    category: str   # 지진 / 화재 / 태풍 / 홍수
    topic: str      # 세부 주제 (예: "소화기 사용법")
    n_questions: int = 5  # 기본 5문제

class QuizQuestionSchema(BaseModel):
    question_text: str
    choices: Dict[str, str]
    correct_answer: str
    difficulty: str

class QuizResponse(BaseModel):
    category: str
    topic: str
    questions: List[QuizQuestionSchema]
