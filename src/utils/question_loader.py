import json
import pathlib
from typing import List

from .data_models import Question

def load_questions_from_jsonl(path: pathlib.Path) -> List[Question]:
    questions: List[Question] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            q = Question(
                id = obj["id"],
                question = obj["question"],
                options = obj["options"],
                correct_option = obj["correct_option"]
            )

            questions.append(q)

    return questions