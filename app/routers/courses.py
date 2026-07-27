import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.course import Course, CourseSession
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.course import CourseCreate, CourseOut, CourseSessionCreate, CourseSessionOut

router = APIRouter(prefix="/courses", tags=["الكورسات"])


@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Course).order_by(Course.title).all()


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.TRAINING_MANAGER)),
):
    if db.query(Course).filter(Course.code == payload.code).first():
        raise HTTPException(status_code=400, detail="كود الكورس مستخدم بالفعل")

    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="الكورس غير موجود")
    return course


@router.get("/{course_id}/sessions", response_model=list[CourseSessionOut])
def list_course_sessions(
    course_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return db.query(CourseSession).filter(CourseSession.course_id == course_id).order_by(
        CourseSession.start_date.desc()
    ).all()


@router.post("/sessions", response_model=CourseSessionOut, status_code=status.HTTP_201_CREATED)
def create_course_session(
    payload: CourseSessionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.TRAINING_MANAGER)),
):
    course = db.get(Course, payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="الكورس غير موجود")

    session_obj = CourseSession(**payload.model_dump())
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj
