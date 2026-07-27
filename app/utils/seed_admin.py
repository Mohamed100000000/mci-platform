"""
سكربت لإنشاء أول مستخدم أدمن في النظام (يُشغَّل مرة واحدة بعد أول migration).

الاستخدام:
    python -m app.utils.seed_admin
"""
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole


def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@azda.local").first()
        if existing:
            print("المستخدم الأدمن موجود بالفعل.")
            return

        admin = User(
            full_name="مدير النظام",
            email="admin@azda.local",
            hashed_password=hash_password("ChangeMe123!"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("تم إنشاء المستخدم الأدمن بنجاح.")
        print("البريد: admin@azda.local | كلمة المرور: ChangeMe123!")
        print("⚠️  غيّر كلمة المرور فورًا بعد أول تسجيل دخول.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
