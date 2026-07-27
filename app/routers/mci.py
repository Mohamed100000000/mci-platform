import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.trainee import Trainee
from app.models.mci_score import MCIScore
from app.models.user import User
from app.schemas.certificate import MCIScoreOut
from app.services.mci_scoring import calculate_mci_score

router = APIRouter(prefix="/mci", tags=["مؤشر الكفاءة البحرية MCI"])


@router.post("/trainees/{trainee_id}/calculate", response_model=MCIScoreOut)
def calculate_and_save_mci_score(
    trainee_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    """يحسب مؤشر MCI الحالي للمتدرب ويحفظه كسجل تاريخي (snapshot)."""
    trainee = db.get(Trainee, trainee_id)
    if not trainee:
        raise HTTPException(status_code=404, detail="المتدرب غير موجود")

    breakdown = calculate_mci_score(db, trainee_id, as_of=date.today())

    score_record = MCIScore(
        trainee_id=trainee_id,
        calculated_on=date.today(),
        total_score=breakdown.total,
        attendance_component=breakdown.attendance_component,
        competency_component=breakdown.competency_component,
        certification_component=breakdown.certification_component,
        recency_component=breakdown.recency_component,
        breakdown=breakdown.details,
    )
    db.add(score_record)
    db.commit()
    db.refresh(score_record)
    return score_record


@router.get("/trainees/{trainee_id}/history", response_model=list[MCIScoreOut])
def get_mci_history(trainee_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(MCIScore)
        .filter(MCIScore.trainee_id == trainee_id)
        .order_by(MCIScore.calculated_on.desc())
        .all()
    )


@router.get("/trainees/{trainee_id}/latest", response_model=MCIScoreOut)
def get_latest_mci_score(
    trainee_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    latest = (
        db.query(MCIScore)
        .filter(MCIScore.trainee_id == trainee_id)
        .order_by(MCIScore.calculated_on.desc())
        .first()
    )
    if not latest:
        raise HTTPException(status_code=404, detail="لا يوجد مؤشر MCI محسوب لهذا المتدرب بعد")
    return latest


@router.get("/leaderboard", response_model=list[MCIScoreOut])
def get_mci_leaderboard(limit: int = 20, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """أعلى المتدربين تصنيفًا بناءً على آخر مؤشر MCI محسوب لكل منهم (تقريبي - آخر السجلات)."""
    return db.query(MCIScore).order_by(MCIScore.total_score.desc()).limit(limit).all()
