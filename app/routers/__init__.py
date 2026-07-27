from fastapi import APIRouter

from app.routers import auth, users, trainees, courses, attendance, competency, certificates, mci

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(trainees.router)
api_router.include_router(trainees.org_router)
api_router.include_router(courses.router)
api_router.include_router(attendance.router)
api_router.include_router(competency.router)
api_router.include_router(certificates.router)
api_router.include_router(mci.router)
