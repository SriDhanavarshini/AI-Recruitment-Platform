from fastapi import APIRouter, HTTPException, status

from app.schemas.schemas import ProctoringEventCreate

router = APIRouter(prefix="/proctoring", tags=["proctoring"])


@router.post("/events")
def create_event(payload: ProctoringEventCreate):
    valid_events = {"FACE_NOT_DETECTED", "MULTIPLE_FACES", "TAB_SWITCH", "FULLSCREEN_EXIT", "CAMERA_DISCONNECTED"}
    if payload.event_type not in valid_events:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported proctoring event type")
    return {"message": "Event stored", "event_type": payload.event_type, "assessment_attempt_id": payload.assessment_attempt_id}
