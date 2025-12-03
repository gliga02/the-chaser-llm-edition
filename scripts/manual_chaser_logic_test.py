import json
import pathlib
import sys
from typing import List

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.data_models import Question
from src.game.chaser_logic import ChaserLogic

def load_sample_questions(path: pathlib.Path, n: int = 3) -> List[Question]:
    questions: List[Question] = []

    with path.open("r", encoding = "utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            obj = json.loads(line)
            q = Question(
                id = obj["id"],
                question = obj["question"],
                options = obj["options"],
                correct_option = obj["correct_option"]
            )

            questions.append(q)

    return questions


def main() -> None:
    questions_path = BASE_DIR / "data" / "processed" / "question_chaser.jsonl"
    if not questions_path:
        print("Questions file not found")
        print("Run the queston preparation pipeline first")
        return
    
    questions = load_sample_questions(questions_path, n = 3)

    chaser = ChaserLogic(model="gpt-4.1-mini", p_correct=0.75)

    for q in questions:
        print("\n============================")
        print(f"Question ID: {q.id}")
        print(q.question)
        print(f"A) {q.options['A']}")
        print(f"B) {q.options['B']}")
        print(f"C) {q.options['C']}")
        print(f"D) {q.options['D']}")
        print(f"[Correct: {q.correct_option}]")

        answer = chaser.answer_in_chase(q)

        print("\n----Chaser result-----")
        print(f"Natural LLM choice: {answer.natural_llm_choice}")
        print(f"Final chosen opton (after error model): {answer.chosen_option}")
        print(f"Is correct (after error model): {answer.is_correct}")
        print("\nRaw LLM response:")
        print(answer.raw_llm_response)


if __name__ == "__main__":
    print("manual_chaser_logic_test.py starting...")
    main()
    print("manual_chaser_logic_test finished")
    