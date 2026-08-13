import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.qbank.enums import GenerationJobStatus, GenerationTaskStatus
from app.qbank.models import QbankGenerationJob
from app.qbank.schemas import GenerationJobCreate, GenerationJobOut, GenerationJobSummary
from app.qbank.services import job_service

_GENERATION_ROLES = (UserRole.ADMIN, UserRole.TRAINING_MANAGER)

router = APIRouter()


def _enqueue_task(task_id: uuid.UUID) -> None:
    """يُجدول مهمة واحدة في طابور RQ بسياسة إعادة محاولة (المرحلة 2B.1
    الأساسية — القيمة تُقرأ من الإعدادات، ليست مضمَّنة). مفصولة في دالة
    مستقلة لسهولة الاستبدال أو المحاكاة في الاختبارات بدون Redis حقيقي."""
    from redis import Redis
    from rq import Queue, Retry

    from app.core.config import settings

    redis_conn = Redis.from_url(settings.QBANK_REDIS_URL)
    queue = Queue("qbank-generation", connection=redis_conn)
    queue.enqueue(
        "app.qbank.workers.generation_worker.run_generation_task",
        str(task_id),
        retry=Retry(max=settings.QBANK_MAX_TASK_RETRIES, interval=[30, 120, 300][: settings.QBANK_MAX_TASK_RETRIES]),
        job_timeout="10m",
    )


@router.post("/generation/jobs", response_model=GenerationJobOut, status_code=201)
def create_generation_job(
    payload: GenerationJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    """يُنشئ job + tasks فورًا مت متزامن، سريع — مجرد صفوف قاعدة بيانات),
    ثم يُجدول كل task في الطابور لتُنفَّذ لاحقًا بواسطة عامل RQ منفصل.
    الاستجابة ترجع فورًا بمعرّف الـjob — لا ينتظر الطلب اكتمال أي توليد فعلي."""
    job = job_service.create_job(db, payload, current_user.id)
    for task in job.tasks:
        _enqueue_task(task.id)
    return job


@router.get("/generation/jobs/{job_id}", response_model=GenerationJobOut)
def get_generation_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    job = db.get(QbankGenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job


@router.get("/generation/jobs/{job_id}/summary", response_model=GenerationJobSummary)
def get_generation_job_summary(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    """نقطة نهاية مخصَّصة لصفحة مراقبة الدفعات (Batch Monitor) لاحقًا —
    ترجع ملخصًا مُجمَّعًا بدون تحميل كل صفوف tasks الكاملة في كل استطلاع (poll)."""
    job = db.get(QbankGenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job_service.get_job_summary(db, job)


@router.get("/generation/jobs", response_model=list[GenerationJobOut])
def list_generation_jobs(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    from sqlalchemy import select

    stmt = select(QbankGenerationJob).where(QbankGenerationJob.course_id == course_id).order_by(
        QbankGenerationJob.created_at.desc()
    )
    return list(db.execute(stmt).scalars().all())


@router.post("/generation/jobs/{job_id}/pause", response_model=GenerationJobOut)
def pause_generation_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    """إيقاف مؤقت: المهام قيد التنفيذ فعليًا (running) تُكمل — لا محاولة
    لقطع استدعاء AI أثناء تنفيذه. المهام التي لم تبدأ بعد (queued) تُتخطى
    عند وصول دورها في العامل (انظر job_service.execute_task)."""
    job = db.get(QbankGenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job_service.pause_job(db, job)


@router.post("/generation/jobs/{job_id}/resume", response_model=GenerationJobOut)
def resume_generation_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*_GENERATION_ROLES)),
):
    job = db.get(QbankGenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    job = job_service.resume_job(db, job)
    for task in job.tasks:
        if task.status == GenerationTaskStatus.QUEUED:
            _enqueue_task(task.id)
    return job
