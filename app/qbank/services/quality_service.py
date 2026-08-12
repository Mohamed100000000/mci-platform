"""
فحوصات جودة قاعدية قبل دخول السؤال المولَّد لطابور المراجعة.

قرار نطاق واعٍ لهذه المرحلة قاول على قواعد صريحة
(rule-based)، وليس استدعاء AI ثانٍ للمراجعة الذاتية. استدعاء AI إضافي لك
سؤال يضاعف التكلفة والزمن قبل إثبات أن خط الأنابيب الأساسي يعمل بشكل صحيح.
"""
from dataclasses import dataclass


@dataclass
class QualityCheckResult:
    score: float  # 0-100
    flags: list[str]


def run_quality_checks(item: dict, interaction_type: str) -> QualityCheckResult:
    flags: list[str] = []
    score = 100.0

    stem = item.get("stem_text", "")
    options = item.get("options", [])

    if len(stem) < 20:
        flags.append("stem قصير جدًا — قد يكون غامضًا")
        score -= 15
    if len(stem) > 800:
        flags.append("stem طويل جدًا - قد يحتاج تبسيطًا")
        score -= 5

    if interaction_type in ("mcq", "multiple_response") and options:
        lengths = [len(o.get("text", "")) for o in options if isinstance(o, dict)]
        if lengths and (max(lengths) - min(lengths)) > 3 * (sum(lengths) / len(lengths) or 1):
            flags.append("uneven option lengths - may hint at the answer")
            score -= 10

    if interaction_type == "mcq" and options:
        correct = [o for o in options if isinstance(o, dict) and o.get("is_correct")]
        others = [o for o in options if isinstance(o, dict) and not o.get("is_correct")]
        if correct and others:
            correct_len = len(correct[0].get("text", ""))
            other_lens = [len(o.get("text", "")) for o in others]
            if other_lens and correct_len > max(other_lens) * 1.5:
                flags.append("correct answer noticeably longer than distractors")
                score -= 10

    if not item.get("explanation") or len(item.get("explanation", "")) < 15:
        flags.append("explanation too short or missing")
        score -= 10

    return QualityCheckResult(score=max(0.0, score), flags=flags)
