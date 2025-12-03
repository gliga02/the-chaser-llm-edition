import pathlib
import sys
import json

from typing import List

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from src.utils.data_models import Question
from src.llm.question_answerer import QuestionAnswerer


def load_simple_question(path: pathlib.Path, n: int = 3) -> List[Question]:
    questions: List[Question] = []

    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            obj = json.loads(line)
            q = Question(
                id = obj["id"],
                question = obj["question"],
                options = obj["options"],
                correct_option=obj["correct_option"]
            )

            questions.append(q)

    return questions


def main() -> None:
    questions_path = BASE_DIR / "data" / "processed" / "question_chaser.jsonl"
    if not questions_path.exists():
        print("Question file not found")
        print("Run the question preparation pipeline first")
        return
    
    questions = load_simple_question(questions_path, n = 3)
    qa = QuestionAnswerer()

    for q in questions:
        print("\n=========================")
        print(f"Question ID: {q.id}")
        print(q.question)
        print(f"A) {q.options['A']}")
        print(f"B) {q.options['B']}")
        print(f"C) {q.options['C']}")
        print(f"D) {q.options['D']}")
        print(f"[Correct: {q.correct_option}]")

        chosen, raw = qa.answer_question(q)
        print(f"\nLLM raw response:\n{raw}")
        print(f"\nParsed choice: {chosen}")


if __name__ == "__main__":
        print("manual_llm_test.py starting...")
        main()
        print("manual_llm_test.py finished.")   