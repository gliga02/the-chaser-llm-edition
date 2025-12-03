from dataclasses import dataclass
from typing import Dict

@dataclass
class Question:
    id: str
    question: str
    options: Dict[str, str]
    correct_option: str