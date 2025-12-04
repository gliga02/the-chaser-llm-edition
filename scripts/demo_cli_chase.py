import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.game.state import GamePhase
from src.game.game_runner import (
    initialize_game,
    get_cash_builder_question,
    advence_cash_builder,
    prepare_chase_offers,
    choose_chase_offer,
    get_next_chase_question_for_state,
    run_chase_step_with_chaser
)

from src.game.chaser_logic import ChaserLogic

def main() -> None:
    print("=====CLI DEMO======")

    state = initialize_game(BASE_DIR)
    chaser = ChaserLogic(model="gpt-4.1-mini", p_correct=0.75)

    print("=====CASH BUILDER=====")

    while state.phase == GamePhase.CASH_BUILDER:
        q = get_cash_builder_question(state)
        if q is None:
            break

        print(f"\n{q.question}")
        print(f"A) {q.options['A']}")
        print(f"B) {q.options['B']}")
        print(f"C) {q.options['C']}")
        print(f"D) {q.options['D']}")

        a = input("Your answer (A/B/C/D): ").strip().upper()
        if a not in ["A", "B", "C", "D"]:
            print("Invalid input. Counting as incorrect")
            a = "X"

        state = advence_cash_builder(state, a)

    print(f"\nYou won: {state.player.correct_answers}")
    base_cash = state.player.correct_answers * 1000
    print(f"Base cash (before offers): {base_cash}")

    print("\n------CHASE OFFERS------")

    offers = prepare_chase_offers(state)

    print(f"Low offer: {offers.low_offer_money}")
    print(f"Middle offer: {offers.mid_offer_money}")
    print(f"High offer: {offers.high_offer_money}")

    choice = input("Choose offer (low/mid/high): ").strip().lower()
    state = choose_chase_offer(state, offers, choice)

    print(f"\nYou chose offer: {state.offers.chosen_offer_money}")
    print(f"Your start position: {state.offers.chosen_start_pos}")
    print(f"Chaser start position: {state.chaser.board_position}")

    print('\n----CHASE-----')

    while state.phase == GamePhase.CHASE:
        q = get_next_chase_question_for_state(state)

        print(f"\nBoard: Player at {state.player.board_position}, Chaser at {state.chaser.board_position}")
        print(f"{q.question}")
        print(f"A) {q.options['A']}")
        print(f"B) {q.options['B']}")
        print(f"C) {q.options['C']}")
        print(f"D) {q.options['D']}")

        a = input("Your answer (A/B/C/D): ").strip().upper()
        if a not in ["A", "B", "C", "D"]:
            print("Invalid input. Counting as incorrect")
            a = "X"

        state.current_question = q
        state, chaser_answer = run_chase_step_with_chaser(state, a, chaser)

        print(f"Chaser chose: {chaser_answer.chosen_option} "
              f"({'correct' if chaser_answer.is_correct else 'wrong'})")
        
        if state.phase != GamePhase.CHASE:
            break

    print("\n-----RESULT-----")
    print(f"Game phase: {state.phase.name}")
    if state.outcome_message:
        print(state.outcome_message)
    print(f"Secured cash: {state.player.secured_cash}")


    print("\nDemo finished")


if __name__ == "__main__":
    main()
