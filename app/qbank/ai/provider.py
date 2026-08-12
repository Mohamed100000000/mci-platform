"""
غلاف رقيق حول Anthropic SDK. الهدف: أي خدمة في qbank تستدعي generate()
هنا فقط — لا تستورد anthropic مباشرة في أي مكان آخر. هذا يجعل استبدال
المزوّد أو محاكاته في الاختبارات نقطة واحدة بدلاً من منتشرة في الكود.
"""
import json

from app.core.config import settings


class GenerationError(Exception):
    """يُرفع عند فشل التوليد أو عدم توفر مفتاح API."""


class AIGenerationResult:
    def __init__(self, raw_json: dict, input_tokens: int, output_tokens: int, model: str):
        self.raw_json = raw_json
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.model = model


def generate(prompt: str) -> AIGenerationResult:
    """يستدعي Anthropic API فعليًا. يرفع GenerationError برسالة واضحة إذا
    كان ANTHROPIC_API_KEY غير مضبوط — بدلاً من فشل صامت أو استخدام مفتاح
    وهمي، حتى يكون واضحًا فورًا في أي بيئة (تطوير محلي بدون مفتاح، مثلاً)
    أن التوليد الفعلي غير متاح الآن."""
    if not settings.ANTHROPIC_API_KEY:
        raise GenerationError(
            "ANTHROPIC_API_KEY غير مضبوط في متغيرات البيئة — لا يمكن تنفيذ توليد فعلي. "
            "اضبط المتغير على الخادم (Railway) لتفعيل هذه الميزة."
        )

    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=settings.QBANK_AI_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    # النموذج مُطالَب بإرجاع JSON صِرف؛ نزيل أي أسوار ```json محتملة احتياطًا.
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GenerationError(f"فشل تحليل استجابة النموذج كـJSON: {exc}") from exc

    return AIGenerationResult(
        raw_json=parsed,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        model=settings.QBANK_AI_MODEL,
    )
