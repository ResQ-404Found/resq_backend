from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.models.user_model import User
from app.services.quiz_service import generate_quiz
from app.schemas.quiz_schema import QuizRequest, QuizResponse

router = APIRouter()

@router.post("/quiz/generate", response_model=QuizResponse)
async def generate_quiz_api(
    request: QuizRequest,
    user: User = Depends(get_current_user)
):
    try:
        questions = generate_quiz(request.category, request.topic, request.n_questions)
        return {
            "category": request.category,
            "topic": request.topic,
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/user/add-quiz-point")
async def add_points(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    try:
        user.point += 10
        session.add(user)   # User 객체 변경을 세션에 반영
        session.commit()
        session.refresh(user)
        return {"message": "포인트가 추가되었습니다.", "total_points": user.point}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))