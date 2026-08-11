"""
حساب content_hash لاكتشاف التكرار الحرفي (exact duplicate) — بدون أي AI.

طبقة التكرار الدلالي (near-duplicate/semantic) عبر embeddings مؤجّلة لمرحلة
قادمة (تحتاج استدعاء AI). هذه الطبقة تعمل بالكامل الآن وتمنع فعليًا إدخال
نفس نص السؤال حرفيًا مرتين لنفس الكورس.
"""
import hashlib
import re


def normalize_text(text: str) -> str:
    """تطبيع نص السؤال قبل التجزئة: حروف صغيرة، إزالة المسافات الزائدة
    وعلامات الترقيم البسيطة — بحيث لا يفلت تكرار حرفي بسبب فروق تنسيق."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def compute_content_hash(stem_text: str, scenario_text: str | None = None) -> str:
    """SHA-256 لنص السؤال (+ السيناريو إن وُجد) بعد التطبيع."""
    combined = normalize_text(stem_text)
    if scenario_text:
        combined += "||" + normalize_text(scenario_text)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()
