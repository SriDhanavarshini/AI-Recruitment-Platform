from fastapi import APIRouter, HTTPException, status

from app.schemas.schemas import QuestionCreate, QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])

questions_db: dict[int, dict] = {}


@router.get("", response_model=list[QuestionOut])
def list_questions():
    return list(questions_db.values())


@router.post("", response_model=QuestionOut)
def create_question(payload: QuestionCreate):
    if len(payload.options) != 4 and payload.type != "CODING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MCQ questions must have exactly 4 options")
    question_id = len(questions_db) + 1
    question = {"id": question_id, "approved": False, **payload.model_dump()}
    questions_db[question_id] = question
    return question


@router.patch("/{question_id}/approve")
def approve_question(question_id: int):
    question = questions_db.get(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    question["approved"] = True
    return {"question_id": question_id, "approved": True}
