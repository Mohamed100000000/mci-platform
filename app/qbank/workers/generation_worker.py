"""
نقطة الدخول التي يستدعيها عامل RQ (RQ worker) لكل مهمة توليد. تعمل في
عملية (process) منفصلة عن خادم API، لذلك تفتح جلسة قاعدة بيانات خاصة بها
بدلاً من استخدام أي جلسة من طلب HTTP — هذا إلزامي عبر حدود العمليات.

إعادة المحاولة (retry) تُدار عبر آلية RQ نفسها (rq.retry.Retry) عند جدولة
المهمة في الطابور (routers/jobs.py)، وليس هنا — هذا الدالة تُنفَّذ محاولة
واحدة فقط؛ RQ يعيد استدعاءها تلقائيًا عند رفعها استثناءً، وفق سياسة الحد
الأقصى المضبوطة وقت الجدولة.
"""
import uuid

from app.core.database import SessionLocal
from app.qbank.ai.provider import GenerationError
from app.qbank.models import QbankGenerationTask


def run_generation_task(task_id: str) -> str:
    """الدالة التي يستدعيها RQ. تأخذ معرّف المهمة كنص (RQ يفضّل أنواعًا
    بسيطة قابلة للتسلسل)، وترجع حالة المهمة النهائية كنص للتأكيد في السجلات.

    ملاحظة تصميم مهمة: generation_service.run_generation_batch() (المرحلة
    2A) لا ترفع استثناء أبدًا عند فشل استدعاء AI — تلتقطه وتُسجّله في
    batch.error_message بتصميم متعمّد من تلك المرحلة. لكي تعمل إعادة
    المحاولة التلقائية لـRQ (التي تعتمد على رفع استثناء)، هذه الدالة تحوّل
    حالة "failed" الناتجة إلى استثناء صريح هنا فقط — طبقة الطابور، بدون أي
    تعديل على دالة 2A نفسها."""
    from app.qbank.services import job_service

    db = SessionLocal()
    try:
        task = db.get(QbankGenerationTask, uuid.UUID(task_id))
        if task is None:
            return "task_not_found"
        if task.retry_count > 0 or task.status.value == "failed":
            task.retry_count += 1
            db.commit()
        result = job_service.execute_task(db, task)
        if result.status.value == "failed":
            raise GenerationError(result.last_error or "Generation task failed")
        return result.status.value
    finally:
        db.close()
