import json
import pathlib
import random
from typing import List
from dataclasses import asdict

import pandas as pd

from .data_models import Question

PROCESSED_CLEAN_CSV_PATH = pathlib.Path("data/processed/cleaned_preview.csv")
PROCESSED_QUESTIONS_PATH = pathlib.Path("data/processed/question_chaser.jsonl")

"""
1. Load one or more raw OpenTriviaQA CSV files from data/raw/.
2. Normalize each row into a Question object with a unified schema.
3. Optionally filter / deduplicate / shuffle questions (later).
4. Save all normalized questions into a single JSONL file under data/processed/.

"""



def normalize_question_row(row: pd.Series, qid: str) -> Question:
    question_text = str(row['Questions']).strip()

    options = {
        "A": str(row['A']).strip(),
        "B": str(row['B']).strip(),
        "C": str(row['C']).strip(),
        "D": str(row['D']).strip()
    }

    correct_str = str(row['Correct']).strip()
    correct_upper = correct_str.upper()

    if correct_upper in ["A", "B", "C", "D"]:
        correct_option = correct_upper

    else:
        correct_option = None
        correct_lower = correct_str.lower()

        for key, text in options.items():
            if text.lower() == correct_lower:
                correct_option = key
                break
        
        if correct_option is None:
            raise ValueError(f"Correct value {correct_str} does not match any option")
        
    return Question(
        id = qid,
        question = question_text,
        options = options,
        correct_option = correct_option
    )

def load_and_normalize_questions(csv_path:pathlib.Path) -> List[Question]:
    df = pd.read_csv(csv_path)

    questions: List[Question] = []
    counter = 1

    for _, row in df.iterrows():
        qid = f"q_{counter:06d}"
        q = normalize_question_row(row, qid)
        questions.append(q)
        counter += 1

    unique_questions: List[Question] = []
    seen_keys = set()

    for q in questions:
        key = (
            q.question,
            q.options["A"],
            q.options["B"],
            q.options["C"],
            q.options["D"]
        )

        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_questions.append(q)

    random.shuffle(unique_questions)

    print(f"Total rows in cleaned csv: {len(questions)}")
    print(f"After dedup: {len(unique_questions)}")

    return unique_questions

def save_questions_to_jsonl(questions: List[Question], output_path: pathlib.Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for q in questions:
            obj = {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "correct_option": q.correct_option,
            }

            f.write(json.dumps(obj, ensure_ascii = False) + "\n")