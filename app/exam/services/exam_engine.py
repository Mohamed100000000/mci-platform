"""
Server-side exam logic. Nothing in this file is ever exposed to the client
directly — routers call these functions and translate the result into the
answer-free Pydantic schemas before responding.
"""

import random
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from models import ExamAnswer, ExamAttempt, AttemptStatus, Level, Question


def pick_questions_for_attempt(db: Session, level: Level) -> List[Question]:
    """
    Randomly select `questions_per_attempt` active questions from the level's
    pool. Pulling a random subset (rather than always the same N) means two
    trainees sitting the same level rarely see an identical paper, which
    defeats "someone photographs question 1-20 and shares them" cheating.
    """
    pool = (
        db.query(Question)
        .options(joinedload(Question.options))
        .filter(Question.level_id == level.id, Question.is_active.is_(True))
        .all()
    )
    if len(pool) < level.questions_per_attempt:
        # Not enough bank depth yet — fall back to whatever exists.
        chosen = pool
    else:
        chosen = random.sample(pool, level.questions_per_attempt)
    random.shuffle(chosen)
    return chosen


def shuffled_options(question: Question):
    opts = list(question.options)
    random.shuffle(opts)
    return opts


def start_attempt(
    db: Session,
    level: Level,
    trainee_name: str,
    trainee_email: str,
    trainee_id_number: str,
    trainee_id: UUID,
    ip_address: str,
    user_agent: str,
) -> ExamAttempt:
    questions = pick_questions_for_attempt(db, level)
    total_time = level.time_limit_seconds * max(len(questions), 1)
    attempt = ExamAttempt(
        trainee_id=trainee_id,
        trainee_name=trainee_name,
        trainee_email=trainee_email,
        trainee_id_number=trainee_id_number,
        level_id=level.id,
        status=AttemptStatus.in_progress,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=total_time + 30),  # +30s network grace
        total_questions=len(questions),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(attempt)
    db.flush()

    # Pre-create empty answer rows so we know exactly which questions belong
    # to this attempt (and in what order) without re-sending the answer key.
    for q in questions:
        db.add(ExamAnswer(attempt_id=attempt.id, question_id=q.id))
    db.commit()
    db.refresh(attempt)
    return attempt


def record_answer(db: Session, attempt: ExamAttempt, question_id: UUID, selected_option_id, time_taken_seconds):
    if attempt.status != AttemptStatus.in_progress:
        raise ValueError("Attempt is not in progress")
    if datetime.now(timezone.utc) > attempt.expires_at.replace(tzinfo=timezone.utc):
        attempt.status = AttemptStatus.expired
        db.commit()
        raise ValueError("Attempt has expired")

    answer = (
        db.query(ExamAnswer)
        .filter(ExamAnswer.attempt_id == attempt.id, ExamAnswer.question_id == question_id)
        .first()
    )
    if answer is None:
        raise ValueError("Question does not belong to this attempt")

    is_correct = False
    if selected_option_id is not None:
        question = db.get(Question, question_id)
        correct_option = next((o for o in question.options if o.is_correct), None)
        is_correct = correct_option is not None and correct_option.id == selected_option_id

    answer.selected_option_id = selected_option_id
    answer.is_correct = is_correct
    answer.time_taken_seconds = time_taken_seconds
    db.commit()
    return answer


def submit_attempt(db: Session, attempt: ExamAttempt) -> ExamAttempt:
    if attempt.status not in (AttemptStatus.in_progress, AttemptStatus.expired):
        raise ValueError("Attempt already finalized")

    answers = attempt.answers
    score = sum(1 for a in answers if a.is_correct)
    total = len(answers)
    pct = round((score / total) * 100) if total else 0

    attempt.score = score
    attempt.total_questions = total
    attempt.pct = pct
    attempt.passed = pct >= attempt.level.pass_threshold_pct
    attempt.status = AttemptStatus.submitted
    attempt.submitted_at = datetime.now(timezone.utc)

    # Update item-analysis counters for question calibration
    for a in answers:
        q = db.get(Question, a.question_id)
        q.times_shown = (q.times_shown or 0) + 1
        if a.is_correct:
            q.times_correct = (q.times_correct or 0) + 1

    db.commit()
    db.refresh(attempt)
    return attempt


def rank_label(pct: int, lang: str = "ar") -> str:
    if pct >= 85:
        return "الربّان ⚓" if lang == "ar" else "The Captain ⚓"
    if pct >= 60:
        return "ضابط بحري" if lang == "ar" else "Marine Officer"
    return "بحّار متدرب" if lang == "ar" else "Trainee Seafarer"
