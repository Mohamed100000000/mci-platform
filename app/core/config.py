"""
إعدادات التطبيق العامة - تُقرأ من متغيرات البيئة (.env)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # عام
    PROJECT_NAME: str = "AZDA Marine Competency Index (MCI) Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # قاعدة البيانات
    DATABASE_URL: str = "postgresql://azda_user:azda_pass@localhost:5432/azda_mci"

    # الأمان / JWT
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 ساعات
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # MCI Scoring
    MCI_SCORE_MIN: int = 0
    MCI_SCORE_MAX: int = 1000

    # AI Question Generation (Phase 2A) — يُقرأ من متغيرات البيئة، لا مفتاح
    # مضمَّن في الكود. إذا كان فارغًا، أي محاولة توليد فعلي تفشل بخطأ واضح
    # بدلاً من التصرف بصمت أو استخدام مفتاح وهمي.
    ANTHROPIC_API_KEY: str = ""
    QBANK_AI_MODEL: str = "claude-sonnet-4-6"
    QBANK_PROMPT_VERSION: str = "v1"

    # طابور التوليد (المرحلة 2B.1) — يُقرأ من متغيرات البيئة، لا قيمة
    # مضمَّنة تُفترض صالحة للإنتاج. القيمة الافتراضية هنا (localhost) تعمل
    # فقط في بيئة تطوير محلية بها Redis يعمل، وليست قيمة إنتاج.
    QBANK_REDIS_URL: str = "redis://localhost:6379/0"
    QBANK_MAX_TASK_RETRIES: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
