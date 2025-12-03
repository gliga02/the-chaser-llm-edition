import random
from dataclasses import dataclass
from typing import Tuple

from src.utils.data_models import Question
from src.llm.question_answerer import QuestionAnswerer

@dataclass
class ChaserAnswer:
    chosen_option: str
    is_correct: bool
    raw_llm_response: str
    natural_llm_choice: str


class ChaserLogic:
    def __init__(self, model: str = "gpt-4.1-mini", p_correct: float = 0.75):
        self.qa = QuestionAnswerer(model = model)
        self.p_correct = p_correct

    def answer_in_chase(self, question: Question) -> ChaserAnswer:
        llm_choice, raw = self.qa.answer_question(question)
        llm_choice = llm_choice.upper()

        force_correct = random.random() < self.p_correct

        if force_correct:
            chosen_option = question.correct_option
            is_correct = True

        else:
            wrong_options = [opt for opt in ["A", "B", "C", "D"] if opt != question.correct_option]
            chosen_option = random.choice(wrong_options)
            is_correct = False

        return ChaserAnswer(
            chosen_option=chosen_option,
            is_correct=is_correct,
            raw_llm_response=raw,
            natural_llm_choice=llm_choice
        )