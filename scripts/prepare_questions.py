"""
- Read raw CSV paths from data/raw/
- Call functions from src.utils.prepare_questions
- Write processed questions to data/processed/

"""

import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from src.utils.prepare_questions import (
    PROCESSED_QUESTIONS_PATH,
    PROCESSED_CLEAN_CSV_PATH,
    load_and_normalize_questions,
    save_questions_to_jsonl
)

def main() -> None:
    if not PROCESSED_CLEAN_CSV_PATH.exists():
        print(f"Cleaned CSV not found")
        print(f"Please run 01_trivia_eda notebook first")
        return
    
    print(f"Loading cleaned data from {PROCESSED_CLEAN_CSV_PATH}")
    questions = load_and_normalize_questions(PROCESSED_CLEAN_CSV_PATH)
    print(f"Normalized questions: {len(questions)}")
    save_questions_to_jsonl(questions, PROCESSED_QUESTIONS_PATH)
    print(f"Processed questions saved to {PROCESSED_QUESTIONS_PATH}")


if __name__ == "__main__":
    main()