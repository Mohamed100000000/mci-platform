from fastapi import APIRouter

from app.qbank.routers import blueprints, generation, jobs, questions, review, sources

router = APIRouter()
router.include_router(questions.router, tags=["qbank-questions"])
router.include_router(review.router, tags=["qbank-review"])
router.include_router(blueprints.router, tags=["qbank-blueprints"])
router.include_router(generation.router, tags=["qbank-generation"])
router.include_router(sources.router, tags=["qbank-sources"])
router.include_router(jobs.router, tags=["qbank-jobs"])
