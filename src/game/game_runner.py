import pathlib
from typing import List, Optional

from src.utils.data_models import Question
from src.utils.question_loader import load_questions_from_jsonl
from .state import GameState
from .engine import (
    start_new_game,
    start_cash_builder,
    get_current_cash_builder_question,
    process_cash_builder_answer,
    generate_chase_offers,
    apply_player_offer_choice,
    get_next_chase_question,
    process_chase_step,
    start_final_chase,
    get_next_final_chase_question_for_player,
    process_final_chase_player_answer,
    get_next_final_chase_question_for_chaser,
    process_final_chase_chaser_answer,
    N_CASH_BUILDER_QUESTION_DEFAULT,
    N_FINAL_PLAYER_QUESTION_DEFAULT,
    N_FINAL_CHASER_QUESTION_DEFAULT
)

from .chaser_logic import ChaserLogic, ChaserAnswer
from src.llm.personas import get_random_persona

def load_default_question_pool(root_dir: pathlib.Path) -> List[Question]:
    path = root_dir / "data" / "processed" / "question_chaser.jsonl"
    if not path.exists():
        raise FileNotFoundError("Question file not found")
    return load_questions_from_jsonl(path)


def initialize_game(root_dir: pathlib.Path) -> GameState:
    questions = load_default_question_pool(root_dir)
    state = start_new_game(questions)
    state.persona = get_random_persona()
    state = start_cash_builder(state, N_CASH_BUILDER_QUESTION_DEFAULT)
    
    return state

def advence_cash_builder(state: GameState, player_answer: str) -> GameState:
    state = process_cash_builder_answer(state, player_answer)

    return state

def get_cash_builder_question(state: GameState) -> Optional[Question]:
    return get_current_cash_builder_question(state)


def prepare_chase_offers(state: GameState):
    offers = generate_chase_offers(state)
    
    return offers

def choose_chase_offer(state: GameState, offers, choice: str) -> GameState:
    state = apply_player_offer_choice(state, offers, choice)

    return state

def get_next_chase_question_for_state(state: GameState) -> Question:
    q = get_next_chase_question(state)

    return q

def run_chase_step_with_chaser(
        state: GameState,
        player_answer: str,
        chaser: ChaserLogic
) -> tuple[GameState, ChaserAnswer, str]:
    
    q = state.current_question
    if q is None:
        raise ValueError("No current question set in state for chase step")
    
    chaser_answer = chaser.answer_in_chase(q)

    normalized_player_answer = player_answer.strip().upper()
    player_correct = (normalized_player_answer == q.correct_option)

    state = process_chase_step(
        state = state,
        player_answer=player_answer,
        chaser_correct=chaser_answer.is_correct
    )

    comment = chaser.generate_comment(question = q, player_correct=player_correct, chaser_answer=chaser_answer, player_answer_option=normalized_player_answer)

    return state, chaser_answer, comment

def start_final_chase_default(state: GameState) -> GameState:
    state = start_final_chase(
        state = state,
        n_player_questions=N_FINAL_PLAYER_QUESTION_DEFAULT,
        n_chaser_questions=N_FINAL_CHASER_QUESTION_DEFAULT
    )

    return state


def advence_final_chase_player(state: GameState, player_answer: str) -> GameState:
    state = process_final_chase_player_answer(state, player_answer)

    return state


def advence_final_chase_chaser(state: GameState, chaser_correct: bool) -> GameState:
    state = process_final_chase_chaser_answer(state, chaser_correct)

    return state