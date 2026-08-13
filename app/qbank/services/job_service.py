"""
خدمة إدارة طابور التوليد (المرحلة 2B.1).

مبدأ أساسي: هذه الخدمة **لا تُعيد تنفيذ منطق التوليد** — هي طبقة تنظيمية
فوق app.qbank.services.generation_service.run_generation_batch() الموجودة
من المرحلة 2A بدون أي تعديل عليها. كل task عند التنفيذ:
  1. تُنشئ صف QbankGenerationBatch (نفس جدول المرحلة 2A، بلا تغيير)
  2. تستدعي generation_service.run_generation_batch() بالضبط كما في 2A
  3. تُحدِّث حالتها وحالة الـjob الأب بناءً على نتيجة الاستدعاء
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.qbank.enums import GenerationBatchStatus, GenerationJobStatus, GenerationTaskStatus
from app.qbank.models import QbankGenerationBatch, QbankGenerationJob, QbankGenerationTask
from app.qbank.schemas import GenerationJobCreate, GenerationJobSummary


def create_job(db: Session, payload: GenerationJobCreate, requested_by_id: uuid.UUID) -> QbankGenerationJob:
    """يُنشئ job واحدة وتفريعها لعدة tasks — بدون تنفيذ أي شيء فعليًا بعد.
    التنفيذ الفعلي يحدث عند enqueue (طبقة الـworker/router، §2B.1 القادمة
    في الـrouter) — هذه الدالة نقية، سهلة الاختبار بمعزل عن الطابور."""
    total_requested = sum(t.count for t in payload.tasks)
    job = QbankGenerationJob(
        course_id=payload.course_id,
        requested_by_id=requested_by_id,
        total_requested=total_requested,
        spec={"tasks": [t.model_dump(mode="json") for t in payload.tasks]},
        status=GenerationJobStatus.QUEUED,
    )
    db.add(job)
    db.flush()

    for task_spec in payload.tasks:
        db.add(
            QbankGenerationTask(
                job_id=job.id,
                learning_objective_id=task_spec.learning_objective_id,
                interaction_type=task_spec.interaction_type.value,
                content_type=task_spec.content_type.value,
                difficulty=task_spec.difficulty.value,
                is_scenario_based=task_spec.is_scenario_based,
                requested_count=task_spec.count,
                source_document_ids=[str(i) for i in task_spec.source_document_ids] or None,
                status=GenerationTaskStatus.QUEUED,
            )
        )

    db.commit()
    db.refresh(job)
    return job


def get_job_summary(db: Session, job: QbankGenerationJob) -> GenerationJobSummary:
    tasks = job.tasks
    return GenerationJobSummary(
        id=job.id,
        status=job.status,
        total_requested=job.total_requested,
        total_generated=job.total_generated,
        tasks_total=len(tasks),
        tasks_completed=sum(1 for t in tasks if t.status == GenerationTaskStatus.COMPLETED),
        tasks_failed=sum(1 for t in tasks if t.status == GenerationTaskStatus.FAILED),
        tasks_running=sum(1 for t in tasks if t.status == GenerationTaskStatus.RUNNING),
        tasks_queued=sum(1 for t in tasks if t.status == GenerationTaskStatus.QUEUED),
    )


def execute_task(db: Session, task: QbankGenerationTask) -> QbankGenerationTask:
    """تُنفَّذ بواسطة الـworker (RQ) لكل مهمة على حدة. يمكن استدعاؤها أيضًا
    مباشرة (بدون طابور) للاختبار المتزامن — وهذا بالضبط ما تفعله اختبارات
    هذه المرحلة، لضمان أن نتيجة التنفيذ عبر الطابور مطابقة تمامًا لنتيجة
    الاستدعاء المباشر من المرحلة 2A."""
    from app.qbank.services import generation_service

    job = db.get(QbankGenerationJob, task.job_id)

    # احترام حالة الإيقاف المؤقت (pause) — إذا أُوقفت اـjob قبل بدء هذه
    # المهمة تحديدًا, تُتخطى بدلاً من تنفيذها. هذا هو أساس دعم pause/resume
    # بدون الحاجة لمحاولة إيقاف استدعاء AI أثناء تنفيذه فعليًا.
    if job.status == GenerationJobStatus.PAUSED:
        task.status = GenerationTaskStatus.SKIPPED
        db.commit()
        return task

    task.status = GenerationTaskStatus.RUNNING
    from sqlalchemy import func

    task.started_at = func.now()
    if job.status == GenerationJobStatus.QUEUED:
        job.status = GenerationJobStatus.RUNNING
    db.commit()

    batch = QbankGenerationBatch(
        course_id=job.course_id,
        learning_objective_id=task.learning_objective_id,
        requested_by_id=job.requested_by_id,
        requested_count=task.requested_count,
        source_document_ids=task.source_document_ids,
        status=GenerationBatchStatus.QUEUED,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    batch = generation_service.run_generation_batch(
        db,
        batch,
        interaction_type=task.interaction_type,
        content_type=task.content_type,
        difficulty=task.difficulty,
        is_scenario_based=task.is_scenario_based,
    )

    task.generation_batch_id = batch.id
    if batch.status == GenerationBatchStatus.COMPLETED:
        task.status = GenerationTaskStatus.COMPLETED
        job.total_generated += batch.generated_count
    else:
        task.status = GenerationTaskStatus.FAILED
        task.last_error = batch.error_message

    task.completed_at = func.now()
    job.total_input_tokens += batch.input_tokens or 0
    job.total_output_tokens += batch.output_tokens or 0
    db.commit()

    _maybe_complete_job(db, job)
    db.refresh(task)
    return task


def _maybe_complete_job(db: Session, job: QbankGenerationJob) -> None:
    """يُحدِّث حالة الـjob الأب إلى completed/failed فقط عندما لا تبقى أي
    مهمة queued أو running — لا تُستدعى مباشرة من الخارج."""
    from sqlalchemy import func

    remaining = db.execute(
        select(QbankGenerationTask).where(
            QbankGenerationTask.job_id == job.id,
            QbankGenerationTask.status.in_([GenerationTaskStatus.QUEUED, GenerationTaskStatus.RUNNING]),
        )
    ).scalars().first()
    if remaining is None and job.status == GenerationJobStatus.RUNNING:
        any_failed = db.execute(
            select(QbankGenerationTask).where(
                QbankGenerationTask.job_id == job.id, QbankGenerationTask.status == GenerationTaskStatus.FAILED
            )
        ).scalars().first()
        job.status = GenerationJobStatus.FAILED if any_failed and job.total_generated == 0 else GenerationJobStatus.COMPLETED
        job.completed_at = func.now()
        db.commit()


def pause_job(db: Session, job: QbankGenerationJob) -> QbankGenerationJob:
    from sqlalchemy import func

    job.status = GenerationJobStatus.PAUSED
    job.paused_at = func.now()
    db.commit()
    db.refresh(job)
    return job


def resume_job(db: Session, job: QbankGenerationJob) -> QbankGenerationJob:
    """يُعيد جدولة المهام queued فقط — المهام المتخطاة (skipped) بسبب
    الإيقاف السابق تعود لـqueued حتى تُلتقط من جديد."""
    from sqlalchemy import func

    for task in job.tasks:
        if task.status == GenerationTaskStatus.SKIPPED:
            task.status = GenerationTaskStatus.QUEUED
    job.status = GenerationJobStatus.QUEUED
    job.resumed_at = func.now()
    db.commit()
    db.refresh(job)
    return job
