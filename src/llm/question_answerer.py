import re
from typing import Tuple

from src.utils.data_models import Question
from .client import OpenAIClient

BASE_SYSTEM_PROMPT = (
    "You are a quiz player. You will always be given a multiple-choice "
    "question with four options: A, B, C, and D.\n"
    "Your task is to pick the single best answer.\n"
    "Always clearly indicate your choice in the format: 'Answer: X' where X is A, B, C, or D."
)

def build_question_prompt(question: Question) -> str:
    lines = [
        "Question:",
        question.question,
        "",
        "Options:",
        f"A) {question.options['A']}",
        f"B) {question.options['B']}",
        f"C) {question.options['C']}",
        f"D) {question.options['D']}",
        "",
        "Please answer in the format: Answer: X",
    ]

    return "\n".join(lines)

def parse_llm_answer(raw_text: str) -> str:
    match = re.search(r"answer\s*:\s*([ABCD])", raw_text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    match = re.search(r"\b([ABCD])\b", raw_text)
    if match:
        return match.group(1).upper()
    
    raise ValueError(f"Could not parse LLM answer from: {raw_text!r}")



class QuestionAnswerer:
    def __init__(self, model: str = "gpt-4.1-mini"):
        self.client = OpenAIClient(model = model)

    def answer_question(self, question: Question) -> Tuple[str, str]:
        user_prompt = build_question_prompt(question)
        raw = self.client.chat(
            system_prompt = BASE_SYSTEM_PROMPT,
            user_prompt = user_prompt
        )

        chosen = parse_llm_answer(raw)
        return chosen, raw