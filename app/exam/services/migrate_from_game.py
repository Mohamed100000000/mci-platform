"""
One-time migration: reads the AZDA Captain Challenge's subjects_data.json
(the same file used to build the standalone HTML game) and inserts it into
the exam database via the models in this module.

Usage
-----
    python -m services.migrate_from_game --json subjects_data.json --institute-id <uuid>

This is meant to run ONCE against your MCI database to seed real question
data instead of the placeholder examples you'd otherwise have to write by
hand. Re-running it is safe: subjects are matched by (institute_id, code)
and skipped if they already exist, so you can re-run after adding new
subjects to the JSON without duplicating existing ones.
"""

import argparse
import json
import sys
from uuid import UUID

from sqlalchemy.orm import Session

# --- adjust these imports to your project's actual layout ---
from models import Difficulty, Institute, Level, Option, Question, Subject
# from app.db.session import SessionLocal
# ---------------------------------------------------------------

DIFFICULTY_BY_INDEX = {0: Difficulty.easy, 1: Difficulty.medium, 2: Difficulty.hard}


def migrate(db: Session, json_path: str, institute_id: UUID) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    institute = db.get(Institute, institute_id)
    if institute is None:
        raise SystemExit(f"Institute {institute_id} not found. Create it first.")

    created_subjects = 0
    created_questions = 0

    for order, (code, subj) in enumerate(data.items()):
        existing = (
            db.query(Subject)
            .filter(Subject.institute_id == institute_id, Subject.code == subj["code"])
            .first()
        )
        if existing:
            print(f"[skip] Subject {subj['code']} already exists")
            continue

        subject_row = Subject(
            institute_id=institute_id,
            code=subj["code"],
            name_ar=subj["name"]["ar"],
            name_en=subj["name"]["en"],
            icon=subj.get("icon"),
            sort_order=order,
        )
        db.add(subject_row)
        db.flush()  # get subject_row.id
        created_subjects += 1

        for level_idx, level_questions in enumerate(subj["levels"]):
            level_row = Level(
                subject_id=subject_row.id,
                index=level_idx,
                difficulty=DIFFICULTY_BY_INDEX[level_idx],
                pass_threshold_pct=60,
                time_limit_seconds=20,
                questions_per_attempt=min(20, len(level_questions)),
            )
            db.add(level_row)
            db.flush()

            for q in level_questions:
                question_row = Question(
                    level_id=level_row.id,
                    text_ar=q["ar"]["q"],
                    text_en=q["en"]["q"],
                )
                db.add(question_row)
                db.flush()
                created_questions += 1

                correct_idx = q["c"]
                for opt_idx, (opt_ar, opt_en) in enumerate(zip(q["ar"]["o"], q["en"]["o"])):
                    db.add(
                        Option(
                            question_id=question_row.id,
                            text_ar=opt_ar,
                            text_en=opt_en,
                            is_correct=(opt_idx == correct_idx),
                            sort_order=opt_idx,
                        )
                    )

    db.commit()
    print(f"Done. Subjects created: {created_subjects}, Questions created: {created_questions}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="Path to subjects_data.json")
    parser.add_argument("--institute-id", required=True, help="UUID of the institute row to attach subjects to")
    args = parser.parse_args()

    # Wire this up to your real session factory:
    # db = SessionLocal()
    print(
        "NOTE: wire `db` up to your project's real SQLAlchemy Session "
        "(see the commented import at the top of this file) before running.",
        file=sys.stderr,
    )
    # migrate(db, args.json, UUID(args.institute_id))
