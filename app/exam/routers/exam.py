"""
FastAPI router: the only HTTP surface the browser talks to during an exam.

Wire-up
-------
    from routers.exam import router as exam_router
    app.include_router(exam_router, prefix="/api/exam", tags=["exam"])

Auth: replace `get_current_trainee` with your project's real auth dependency
(MCI already has JWT auth — reuse it here instead of accepting a bare email
in the request body for production use).
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from models import (
    AttemptStatus,
    Certificate,
    ExamAttempt,
    Level,
    Question,
    Subject,
)
from schemas import (
    CertificateVerifyOut,
    CheatSignalRequest,
    ExamResultOut,
    ExamSessionOut,
    LevelOut,
    OptionOut,
    QuestionOut,
    StartExamRequest,
    SubjectOut,
    SubmitAnswerAck,
    SubmitAnswerRequest,
)
from services.exam_engine import (
    rank_label,
    record_answer,
    shuffled_options,
    start_attempt,
    submit_attempt,
)
from services.certificate_generator import generate_certificate_pdf, make_verification_code

# --- adjust to your project's real dependencies ---
# from app.db.session import get_db
# from app.auth.deps import get_current_trainee
def get_db():
    raise NotImplementedError("Wire this up to your project's DB session dependency")


def get_current_trainee():
    raise NotImplementedError("Wire this up to your project's auth dependency")
# ----------------------------------------------------

router = APIRouter()


@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(institute_id: UUID, db: Session = Depends(get_db)):
    return (
        db.query(Subject)
        .filter(Subject.institute_id == institute_id, Subject.is_active.is_(True))
        .order_by(Subject.sort_order)
        .all()
    )


@router.get("/subjects/{subject_id}/levels", response_model=List[LevelOut])
def list_levels(subject_id: UUID, db: Session = Depends(get_db)):
    return db.query(Level).filter(Level.subject_id == subject_id).order_by(Level.index).all()


@router.post("/start", response_model=ExamSessionOut)
def start_exam(
    payload: StartExamRequest,
    request: Request,
    lang: str = "ar",
    db: Session = Depends(get_db),
    trainee=Depends(get_current_trainee),
):
    level = db.get(Level, payload.level_id)
    if level is None:
        raise HTTPException(404, "Level not found")

    attempt = start_attempt(
        db=db,
        level=level,
        trainee_name=payload.trainee_name,
        trainee_email=payload.trainee_email,
        trainee_id_number=payload.trainee_id_number,
        trainee_id=trainee.id,
        ip_address=request.client.host if request.client else "",
        user_agent=request.headers.get("user-agent", ""),
    )

    questions_out = []
    for answer in attempt.answers:
        q = db.query(Question).options(joinedload(Question.options)).get(answer.question_id)
        opts = shuffled_options(q)
        questions_out.append(
            QuestionOut(
                id=q.id,
                text=q.text_ar if lang == "ar" else q.text_en,
                options=[
                    OptionOut(id=o.id, text=(o.text_ar if lang == "ar" else o.text_en)) for o in opts
                ],
            )
        )

    return ExamSessionOut(
        attempt_id=attempt.id,
        subject_code=level.subject.code,
        level_index=level.index,
        expires_at=attempt.expires_at,
        time_limit_seconds_per_question=level.time_limit_seconds,
        questions=questions_out,
    )


@router.post("/{attempt_id}/answer", response_model=SubmitAnswerAck)
def submit_answer(
    attempt_id: UUID,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    trainee=Depends(get_current_trainee),
):
    attempt = db.get(ExamAttempt, attempt_id)
    if attempt is None or attempt.trainee_id != trainee.id:
        raise HTTPException(404, "Attempt not found")
    try:
        record_answer(
            db, attempt, payload.question_id, payload.selected_option_id, payload.time_taken_seconds
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    return SubmitAnswerAck(question_id=payload.question_id)


@router.post("/{attempt_id}/cheat-signal")
def cheat_signal(attempt_id: UUID, payload: CheatSignalRequest, db: Session = Depends(get_db)):
    """Best-effort anti-cheat telemetry. Not bulletproof (nothing client-side
    ever is) but flags attempts for human review rather than silently trusting
    the client."""
    attempt = db.get(ExamAttempt, attempt_id)
    if attempt is None:
        raise HTTPException(404, "Attempt not found")
    if payload.event == "tab_hidden":
        attempt.tab_switch_count += 1
    elif payload.event == "fullscreen_exit":
        attempt.fullscreen_exit_count += 1
    if attempt.tab_switch_count + attempt.fullscreen_exit_count >= 3:
        attempt.flagged_for_review = True
    db.commit()
    return {"ok": True}


@router.post("/{attempt_id}/submit", response_model=ExamResultOut)
def submit_exam(
    attempt_id: UUID,
    lang: str = "ar",
    db: Session = Depends(get_db),
    trainee=Depends(get_current_trainee),
):
    attempt = db.get(ExamAttempt, attempt_id)
    if attempt is None or attempt.trainee_id != trainee.id:
        raise HTTPException(404, "Attempt not found")
    try:
        attempt = submit_attempt(db, attempt)
    except ValueError as e:
        raise HTTPException(400, str(e))

    cert_id = None
    cert_url = None
    # Certificates are withheld from flagged attempts pending human review.
    if attempt.passed and not attempt.flagged_for_review:
        code = make_verification_code()
        cert = Certificate(attempt_id=attempt.id, verification_code=code)
        db.add(cert)
        db.commit()
        db.refresh(cert)
        pdf_path = generate_certificate_pdf(db, cert)
        cert.pdf_path = pdf_path
        db.commit()
        cert_id = cert.id
        cert_url = f"/api/exam/certificates/{cert.id}/pdf"

    return ExamResultOut(
        attempt_id=attempt.id,
        score=attempt.score,
        total_questions=attempt.total_questions,
        pct=attempt.pct,
        passed=attempt.passed,
        rank_label=rank_label(attempt.pct, lang),
        certificate_id=cert_id,
        certificate_url=cert_url,
    )


@router.get("/verify/{code}", response_model=CertificateVerifyOut)
def verify_certificate(code: str, db: Session = Depends(get_db)):
    """Public endpoint — no auth. This is the QR-code landing page target
    so an employer/auditor can verify a printed certificate is genuine."""
    cert = db.query(Certificate).filter(Certificate.verification_code == code).first()
    if cert is None:
        return CertificateVerifyOut(valid=False)
    attempt = cert.attempt
    level = attempt.level
    return CertificateVerifyOut(
        valid=not cert.revoked,
        trainee_name=attempt.trainee_name,
        subject_name_en=level.subject.name_en,
        level_difficulty=level.difficulty.value,
        pct=attempt.pct,
        issued_at=cert.issued_at,
        institute_name=level.subject.institute.name_en,
        revoked=cert.revoked,
    )
