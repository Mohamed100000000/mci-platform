import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.enrollment import Enrollment
from app.models.attendance import Attendance
from app.models.user import User
from app.schemas.attendance import (
    EnrollmentCreate,
    EnrollmentOut,
    AttendanceCreate,
    AttendanceOut,
    AttendanceBulkCreate,
)

router = APIRouter(tags=["الحضور والتسجيل"])


@router.post("/enrollments", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    payload: EnrollmentCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    enrollment = Enrollment(**payload.model_dump())
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/sessions/{session_id}/enrollments", response_model=list[EnrollmentOut])
def list_session_enrollments(
    session_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return db.query(Enrollment).filter(Enrollment.session_id == session_id).all()


@router.post("/attendance", response_model=AttendanceOut, status_code=status.HTTP_201_CREATED)
def record_attendance(
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = Attendance(**payload.model_dump(), recorded_by_id=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/attendance/bulk", response_model=list[AttendanceOut], status_code=status.HTTP_201_CREATED)
def record_attendance_bulk(
    payload: AttendanceBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """تسجيل حضور دفعة من المتدربين لنفس الجلسة والتاريخ دفعة واحدة (Unified Attendance Entry)."""
    created_records = []
    for item in payload.records:
        record = Attendance(
            trainee_id=item["trainee_id"],
            session_id=payload.session_id,
            attendance_date=payload.attendance_date,
            status=item.get("status", "present"),
            notes=item.get("notes"),
            recorded_by_id=current_user.id,
        )
        db.add(record)
        created_records.append(record)

    db.commit()
    for record in created_records:
        db.refresh(record)
    return created_records


@router.get("/sessions/{session_id}/attendance", response_model=list[AttendanceOut])
def list_session_attendance(
    session_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return db.query(Attendance).filter(Attendance.session_id == session_id).all()
