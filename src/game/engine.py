import random

from typing import List, Optional

from src.utils.data_models import Question
from .state import GameState, GamePhase, OfferState

N_CASH_BUILDER_QUESTION_DEFAULT = 8
CASH_PER_CORRECT = 1_000

BOARD_P_MID = 4
BOARD_P_LOW = 3
BOARD_P_HIGH = 5

LOW_MULT_MIN = 0.25
LOW_MULT_MAX = 0.75
LOW_OFFER_MINIMUM = 500

HIGH_MULT_MIN = 1.5
HIGH_MULT_MAX = 4.0

N_FINAL_PLAYER_QUESTION_DEFAULT = 10
N_FINAL_CHASER_QUESTION_DEFAULT = 10


def start_new_game(question_pool: List[Question]) -> GameState:
    """
    Initialize a new game with a given pool of questions.
    Starts in the CASH_BUILDER phase.
    """
    state = GameState()
    state.phase = GamePhase.CASH_BUILDER
    state.question_pool = list(question_pool)
    state.current_question = None
    state.outcome_message = None

    state.player = state.player.__class__()
    state.chaser = state.chaser.__class__()

    state.cash_builder = state.cash_builder.__class__()
    state.chase = state.chase.__class__()
    state.final_chase = state.final_chase.__class__()
    state.offers = state.offers.__class__()

    return state


# ---------- CASH BUILDER PHASE ----------


def start_cash_builder(state: GameState, n_questions: int) -> GameState:
    """
    Select a subset of questions for the Cash Builder phase and
    reset relevant counters.
    """
    if not state.question_pool:
        raise ValueError("Question pool is empty. Cannot start Cash Builder")
    
    n = min(n_questions, len(state.question_pool))
    selected = random.sample(state.question_pool, n)

    state.cash_builder.questions = selected
    state.cash_builder.current_index = 0

    state.player.correct_answers = 0
    state.phase = GamePhase.CASH_BUILDER

    state.current_question = selected[0] if selected else None

    return state


def get_current_cash_builder_question(state: GameState) -> Optional[Question]:
    """
    Return the current Cash Builder question, or None if finished.
    """
    questions = state.cash_builder.questions
    idx = state.cash_builder.current_index

    if not questions or idx >= len(questions):
        return None
    
    return questions[idx]


def process_cash_builder_answer(state: GameState, player_answer: str) -> GameState:
    """
    Process the player's answer in the Cash Builder phase.

    - Update cash_builder_points.
    - Advance to the next question or move to the next phase.
    """
    current_q = get_current_cash_builder_question(state)
    if current_q is None:
        return state
    
    normalized_answer = player_answer.strip().upper()

    if normalized_answer == current_q.correct_option:
        state.player.correct_answers += 1

    state.cash_builder.current_index += 1

    next_q = get_current_cash_builder_question(state)
    if next_q is None:
        state.phase = GamePhase.CHASE
        state.current_question = None
    else:
        state.current_question = next_q

    return state


# ---------- CHASE (BOARD) PHASE ----------


def generate_chase_offers(state: GameState) -> OfferState:
    """
    Generate low/middle/high offers (money and positions) for the Chase phase,
    based on the Cash Builder result.
    """
    correct_answers = state.player.correct_answers
    base_cash = correct_answers * CASH_PER_CORRECT

    if base_cash <= 0:
        base_cash = CASH_PER_CORRECT

    mid_offer_money = base_cash

    low_mult = random.uniform(LOW_MULT_MIN, LOW_MULT_MAX)
    low_offer_money = round(base_cash * low_mult)
    low_offer_money = max(low_offer_money, LOW_OFFER_MINIMUM)

    high_mult = random.uniform(HIGH_MULT_MIN, HIGH_MULT_MAX)
    high_offer_money = round(base_cash * high_mult)

    offers = OfferState(
        low_offer_money=low_offer_money,
        mid_offer_money=mid_offer_money,
        high_offer_money=high_offer_money,
        low_start_pos=BOARD_P_LOW,
        mid_start_pos=BOARD_P_MID,
        high_start_pos=BOARD_P_HIGH
    )

    return offers


def apply_player_offer_choice(state: GameState, offers: OfferState, choice: str) -> GameState:
    """
    Apply the player's choice of offer: "low", "mid", or "high".

    - Set player's starting position on the board.
    - Set chaser's starting position.
    - Set the chosen offer amount.
    - Move the game phase to CHASE.
    """
    c = choice.strip().lower()

    if c == "low":
        chosen_money = offers.low_offer_money
        chosen_pos = offers.low_start_pos
    elif c == "high":
        chosen_money = offers.high_offer_money
        chosen_pos = offers.high_start_pos
    else:
        chosen_money = offers.mid_offer_money
        chosen_pos = offers.mid_start_pos

    offers.chosen_offer_money = chosen_money
    offers.chosen_start_pos = chosen_pos

    state.offers = offers

    state.player.board_position = chosen_pos

    chaser_start = offers.mid_start_pos + state.chase.chaser_distance
    state.chaser.board_position = chaser_start

    state.phase = GamePhase.CHASE
    state.current_question = None

    return state



def get_next_chase_question(state: GameState) -> Question:
    """
    Select the next question for the Chase phase.
    """
    used_ids = set(state.chase.question_ids_used)
    available = [q for q in state.question_pool if q.id not in used_ids]

    if not available:
        available = state.question_pool

    if not available:
        raise ValueError("Question pool is empty, cannot get chase questions")
    
    q = random.choice(available)
    state.chase.question_ids_used.append(q.id)
    state.current_question = q

    return q


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
    q = state.current_question
    if q is None:
        return state
    
    normalized_answer = player_answer.strip().upper()
    player_correct = (normalized_answer == q.correct_option)

    if player_correct and state.player.board_position is not None:
        state.player.board_position -= 1

    if chaser_correct and state.chaser.board_position is not None:
        state.chaser.board_position -= 1

    player_pos = state.player.board_position
    chaser_pos = state.chaser.board_position

    if player_pos is not None and player_pos <= 0:
        secured = state.offers.chosen_offer_money or 0
        state.player.secured_cash = secured
        state.phase = GamePhase.FINAL_CHASE
        state.current_question = None
        state.outcome_message = f"Player secured {secured}"
        return state
    
    if player_pos is not None and chaser_pos is not None and chaser_pos <= player_pos:
        state.player.secured_cash = 0
        state.phase = GamePhase.COMPLETED
        state.current_question = None
        state.outcome_message = "The chaser caught the player. Game Over."
        return state
    
    state.current_question = None
    return state


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
    if not state.question_pool:
        raise ValueError("Question pool is empty")
    
    n_p = min(n_player_questions, len(state.question_pool))
    player_qs = random.sample(state.question_pool, n_p)

    n_c = min(n_chaser_questions, len(state.question_pool))
    chaser_qs = random.sample(state.question_pool, n_c)

    state.final_chase.player_questions = player_qs
    state.final_chase.chaser_questions = chaser_qs

    state.final_chase.player_current_index = 0
    state.final_chase.chaser_current_index = 0

    state.player.final_chase_score = 0
    state.chaser.final_chase_score = 0

    state.phase = GamePhase.FINAL_CHASE
    state.current_question = None
    state.outcome_message = None

    return state


def get_next_final_chase_question_for_player(state: GameState) -> Optional[Question]:
    """
    Return the next Final Chase question for the player, or None if finished.
    """
    idx = state.final_chase.player_current_index
    qs = state.final_chase.player_questions

    if idx >= len(qs):
        return None
    
    q = qs[idx]
    state.current_question = q

    return q


def process_final_chase_player_answer(state: GameState, player_answer: str) -> GameState:
    """
    Process the player's answer in the Final Chase.
    - Increment player's final_chase_score if correct.
    - Advance player question index.
    """
    q = get_next_final_chase_question_for_player(state)
    if q is None:
        return None
    
    normalized_answer = player_answer.strip().upper()
    if normalized_answer == q.correct_option:
        state.player.final_chase_score += 1

    state.final_chase.player_current_index += 1
    state.current_question = None

    return state


def get_next_final_chase_question_for_chaser(state: GameState) -> Optional[Question]:
    """
    Return the next Final Chase question for the chaser, or None if finished.
    """
    idx = state.final_chase.chaser_current_index
    qs = state.final_chase.chaser_questions

    if idx >= len(qs):
        return None
    
    q = qs[idx]
    state.current_question = q

    return q


def process_final_chase_chaser_answer(state: GameState, chaser_correct: bool) -> GameState:
    """
    Process the chaser's (LLM) correctness in the Final Chase.
    - Increment chaser's final_chase_score if chaser_correct.
    - Advance chaser question index.
    - When both player and chaser are finished, determine final outcome and set phase=COMPLETED.
    """
    q = get_next_final_chase_question_for_chaser(state)
    if q is not None:
        pass
    else:
        if chaser_correct:
            state.chaser.final_chase_score += 1
        state.final_chase.chaser_current_index += 1

    player_done = state.final_chase.player_current_index >= len(state.final_chase.player_questions)
    chaser_done = state.final_chase.chaser_current_index >= len(state.final_chase.chaser_questions)

    if player_done and chaser_done:
        ps = state.player.final_chase_score
        cs = state.chaser.final_chase_score

        if ps > cs:
            state.outcome_message("Player wins the final chase")

        else:
            state.outcome_message("Chaser wins the final chase")

        state.phase = GamePhase.COMPLETED
        state.current_question = None

    return state
