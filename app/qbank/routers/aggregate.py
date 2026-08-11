from fastapi import APIRouter

from app.qbank.routers import blueprints, questions, review

router = APIRouter()
router.include_router(questions.router, tags=["qbank-questions"])
router.include_router(review.router, tags=["qbank-review"])
router.include_router(blueprints.router, tags=["qbank-blueprints"])
