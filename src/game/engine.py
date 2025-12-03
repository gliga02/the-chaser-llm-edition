from typing import List, Optional

from src.utils.data_models import Question
from .state import GameState, GamePhase, OfferState


def start_new_game(question_pool: List[Question]) -> GameState:
    """
    Initialize a new game with a given pool of questions.
    Starts in the CASH_BUILDER phase.
    """
    raise NotImplementedError


# ---------- CASH BUILDER PHASE ----------


def start_cash_builder(state: GameState, n_questions: int) -> GameState:
    """
    Select a subset of questions for the Cash Builder phase and
    reset relevant counters.
    """
    raise NotImplementedError


def get_current_cash_builder_question(state: GameState) -> Optional[Question]:
    """
    Return the current Cash Builder question, or None if finished.
    """
    raise NotImplementedError


def process_cash_builder_answer(state: GameState, player_answer: str) -> GameState:
    """
    Process the player's answer in the Cash Builder phase.

    - Update cash_builder_points.
    - Advance to the next question or move to the next phase.
    """
    raise NotImplementedError


# ---------- CHASE (BOARD) PHASE ----------


def generate_chase_offers(state: GameState) -> OfferState:
    """
    Generate low/middle/high offers (money and positions) for the Chase phase,
    based on the Cash Builder result.
    """
    raise NotImplementedError


def apply_player_offer_choice(state: GameState, offers: OfferState, choice: str) -> GameState:
    """
    Apply the player's choice of offer: "low", "mid", or "high".

    - Set player's starting position on the board.
    - Set chaser's starting position.
    - Set the chosen offer amount.
    - Move the game phase to CHASE.
    """
    raise NotImplementedError


def get_next_chase_question(state: GameState) -> Question:
    """
    Select the next question for the Chase phase.
    """
    raise NotImplementedError


def process_chase_step(
    state: GameState,
    player_answer: str,
    chaser_correct: bool,
) -> GameState:
    """
    Process a single step in the Chase phase.

    - Evaluate the player's answer (correct / incorrect).
    - Move player towards the bank if correct.
    - Move chaser towards the player if chaser_correct is True.
    - Check win/lose conditions for the Chase.
    - If the player wins, update secured_cash and prepare for Final Chase.
    """
    raise NotImplementedError


# ---------- FINAL CHASE PHASE ----------


def start_final_chase(
    state: GameState,
    n_player_questions: int,
    n_chaser_questions: int,
) -> GameState:
    """
    Initialize the Final Chase phase:
    - Select question sequences for player and chaser.
    - Reset counters and scores.
    """
    raise NotImplementedError


def get_next_final_chase_question_for_player(state: GameState) -> Optional[Question]:
    """
    Return the next Final Chase question for the player, or None if finished.
    """
    raise NotImplementedError


def process_final_chase_player_answer(state: GameState, player_answer: str) -> GameState:
    """
    Process the player's answer in the Final Chase.
    - Increment player's final_chase_score if correct.
    - Advance player question index.
    """
    raise NotImplementedError


def get_next_final_chase_question_for_chaser(state: GameState) -> Optional[Question]:
    """
    Return the next Final Chase question for the chaser, or None if finished.
    """
    raise NotImplementedError


def process_final_chase_chaser_answer(state: GameState, chaser_correct: bool) -> GameState:
    """
    Process the chaser's (LLM) correctness in the Final Chase.
    - Increment chaser's final_chase_score if chaser_correct.
    - Advance chaser question index.
    - When both player and chaser are finished, determine final outcome and set phase=COMPLETED.
    """
    raise NotImplementedError
