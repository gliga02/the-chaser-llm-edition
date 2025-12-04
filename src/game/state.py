from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

from src.utils.data_models import Question
from src.llm.personas import ChaserPersona

class GamePhase(Enum):
    CASH_BUILDER = auto()
    CHASE = auto()
    FINAL_CHASE = auto()
    COMPLETED = auto()


@dataclass
class PlayerState:
    name: str = "Player"
    secured_cash: int = 0
    correct_answers: int = 0
    board_position: Optional[int] = None
    final_chase_score: int = 0

@dataclass
class ChaserState:
    name: str = "The Chaser"
    board_position: Optional[int] = None
    final_chase_score: int = 0

@dataclass
class OfferState:
    low_offer_money: int = 0
    mid_offer_money: int = 0
    high_offer_money: int = 0

    low_start_pos: int = 0
    mid_start_pos: int = 0
    high_start_pos: int = 0

    chosen_offer_money: Optional[int] = None
    chosen_start_pos: Optional[int] = None

@dataclass
class CashBuilderState:
    questions: List[Question] = field(default_factory = list)
    current_index: int = 0


@dataclass
class ChaseState:
    board_steps: int = 7
    chaser_distance: int = 2
    question_ids_used: List[str] = field(default_factory = list)

@dataclass
class FinalChaseState:
    player_questions: List[Question] = field(default_factory= list)
    chaser_questions: List[Question] = field(default_factory= list)
    player_current_index: int = 0
    chaser_current_index: int = 0

@dataclass
class GameState:
    phase: GamePhase = GamePhase.CASH_BUILDER

    persona: Optional[ChaserPersona] = None

    player: PlayerState = field(default_factory=PlayerState)
    chaser: ChaserState = field(default_factory=ChaserState)

    cash_builder: CashBuilderState = field(default_factory=CashBuilderState)
    chase: ChaseState = field(default_factory = ChaseState)
    final_chase: FinalChaseState = field(default_factory=FinalChaseState)
    offers: OfferState = field(default_factory=OfferState)

    question_pool: List[Question] = field(default_factory = list)
    current_question: Optional[Question] = None
    outcome_message: Optional[str] = None