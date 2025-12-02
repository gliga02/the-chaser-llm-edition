import pathlib
from typing import List

import pandas as pd

from .data_models import Question

PROCESSED_QUESTIONS_PATH = pathlib.Path("data/processed/question_chaser.jsonl")

"""
1. Load one or more raw OpenTriviaQA CSV files from data/raw/.
2. Normalize each row into a Question object with a unified schema.
3. Optionally filter / deduplicate / shuffle questions (later).
4. Save all normalized questions into a single JSONL file under data/processed/.

"""


def load_raw_open_trivia_csv(path: pathlib.Path) -> pd.DataFrame:
    raise NotImplementedError


def normalize_question_row(row: pd.Series) -> Question:
    raise NotImplementedError

def load_and_normalize_questions(csv_paths: List[pathlib.Path]) -> List[Question]:
    raise NotImplementedError


def save_questions_to_jsonl(question: List[Question], output_path: pathlib.Path) -> None:
    raise NotImplementedError