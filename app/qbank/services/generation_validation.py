"""
تحقق صارم من مخرجات الـAI الخام قبل تحويلها لصفوف قاعدة بيانات. أي سؤال
لا يجتاز هذا التحقق يُرفض بالكامل (لا يدخل حتى كـdraft) ويُسجَّل في
generation_batch.error_message كسبب رفض — لا "تصحيح تلقائي صامت".
"""
from dataclasses import dataclass

_MIN_STEM_LEN = 10
_MAX_STEM_LEN = 2000

_INTERACTION_RULES = {
    "mcq": {"min_options": 4, "max_options": 4, "min_correct": 1, "max_correct": 1},
    "true_false": {"min_options": 2, "max_options": 2, "min_correct": 1, "max_correct": 1},
    "multiple_response": {"min_options": 4, "max_options": 6, "min_correct": 2, "max_correct": 4},
    "matching": {"min_options": 4, "max_options": 6, "min_correct": 0, "max_correct": 999},
    "ordering": {"min_options": 4, "max_options": 6, "min_correct": 0, "max_correct": 999},
}


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


def validate_generated_question(item: dict, interaction_type: str) -> ValidationResult:
    errors: list[str] = []

    stem = item.get("stem_text")
    if not isinstance(stem, str) or not (_MIN_STEM_LEN <= len(stem.strip()) <= _MAX_STEM_LEN):
        errors.append(f"stem_text مفقود أو خارج الطول المسموح ({_MIN_STEM_LEN}-{_MAX_STEM_LEN} حرف)")

    options = item.get("options")
    if not isinstance(options, list):
        errors.append("options مفقود أو ليس قائمة")
        return ValidationResult(is_valid=False, errors=errors)

    rules = _INTERACTION_RULES.get(interaction_type)
    if not rules:
        errors.append(f"interaction_type غير معروف: {interaction_type}")
        return ValidationResult(is_valid=False, errors=errors)

    if not (rules["min_options"] <= len(options) <= rules["max_options"]):
        errors.append(
            f"عدد الخيارات {len(options)} خارج النطاق المسموح لـ{interaction_type} "
            f"({rules['min_options']}-{rules['max_options']})"
        )

    seen_texts = set()
    correct_count = 0
    for i, opt in enumerate(options):
        if not isinstance(opt, dict) or not isinstance(opt.get("text"), str) or not opt["text"].strip():
            errors.append(f"الخيار رقم {i + 1} بدون نص صالح")
            continue
        if opt["text"].strip().lower() in seen_texts:
            errors.append(f"خيار مكرر: {opt['text']}")
        seen_texts.add(opt["text"].strip().lower())

        if interaction_type in ("matching",) and not opt.get("match_text"):
            errors.append(f"الخيار رقم {i + 1} بدون match_text (مطلوب لأسئلة المطابقة)")
        if interaction_type in ("ordering",) and opt.get("order_position") is None:
            errors.append(f"الخيار رقم {i + 1} بدون order_position (مطلوب لأسئلة الترتيب)")
        if opt.get("is_correct") is True:
            correct_count += 1

    if interaction_type in ("mcq", "true_false", "multiple_response"):
        if not (rules["min_correct"] <= correct_count <= rules["max_correct"]):
            errors.append(
                f"عدد الإجابات الصحيحة {correct_count} خارج النطاق المسموح "
                f"({rules['min_correct']}-{rules['max_correct']}) لـ{interaction_type}"
            )

    if not item.get("explanation"):
        errors.append("explanation مفقود — مطلوب لكل سؤال")

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)
