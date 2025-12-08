import pathlib
import gradio as gr

from src.game.game_runner import (
    initialize_game,
    get_cash_builder_question,
    advence_cash_builder,
    prepare_chase_offers,
    choose_chase_offer,
    get_next_chase_question_for_state,
    run_chase_step_with_chaser,
    start_final_chase_default,
    advence_final_chase_player,
    advence_final_chase_chaser,
    get_final_chase_player_question
)
from src.game.state import GameState, GamePhase
from src.game.chaser_logic import ChaserLogic


def create_app(root_dir: pathlib.Path) -> gr.Blocks:
    """
    Create and return the Gradio Blocks app for The Chaser.
    """

    with gr.Blocks(title="The Chaser – LLM Edition") as demo:
        # ---------- Hidden / internal state ----------
        root_dir_state = gr.State(str(root_dir))
        game_state = gr.State()          # will hold GameState
        chaser_logic_state = gr.State()  # will hold ChaserLogic instance

        # ---------- Header ----------
        gr.Markdown("# The Chaser – LLM Edition")
        gr.Markdown(
            "Single-player version of the quiz **The Chase**, powered by LLMs.\n\n"
            "Click **Start new game** to begin."
        )

        start_new_game_btn = gr.Button("Start new game")

        # ---------- High-level status row ----------
        with gr.Row():
            current_phase_md = gr.Markdown("**Phase:** –")
            current_persona_md = gr.Markdown("**Chaser persona:** –")
            secured_cash_md = gr.Markdown("**Secured cash:** 0")

        # ---------- Cash Builder tab ----------
        with gr.Tab("Cash Builder"):
            gr.Markdown("### Phase 1 – Cash Builder")

            with gr.Group():
                cash_builder_question_md = gr.Markdown("Question will appear here.")
                cash_builder_options = gr.Radio(
                    choices=["A", "B", "C", "D"],
                    label="Your answer",
                    interactive=True,
                )
                cash_builder_submit_btn = gr.Button("Submit answer")
                cash_builder_feedback_md = gr.Markdown("Feedback will appear here.")
                cash_builder_progress_md = gr.Markdown("Correct answers: 0")

                offer_choice_radio = gr.Radio(
                    choices = ["low", "mid", "high"],
                    label = "Choose your offer",
                    interactive=True
                )

                offer_confirm_btn = gr.Button("Confirm offer and go to chase")

        # ---------- Chase tab ----------
        with gr.Tab("Chase"):
            gr.Markdown("### Phase 2 – The Chase (Head-to-Head)")

            with gr.Group():
                board_status_md = gr.Markdown("Board: Player at –, Chaser at –")
                chase_question_md = gr.Markdown("Question will appear here.")
                chase_options = gr.Radio(
                    choices=["A", "B", "C", "D"],
                    label="Your answer",
                    interactive=True,
                )
                chase_submit_btn = gr.Button("Submit answer")

                with gr.Row():
                    chaser_choice_md = gr.Markdown("**Chaser choice:** –")
                    chaser_correct_md = gr.Markdown("**Chaser correct?:** –")

                chaser_comment_md = gr.Markdown("_Chaser comment will appear here._")
                chase_status_md = gr.Markdown("Chase status will appear here.")

        # ---------- Final Chase placeholder tab ----------
        with gr.Tab("Final Chase"):
            gr.Markdown("### Phase 3 – Final Chase")

            with gr.Group():
                final_start_btn = gr.Button("Start Final Chase")

                final_question_md = gr.Markdown("Final chase question will appear here")
                final_options = gr.Radio(
                    choices = ["A", "B", "C", "D"],
                    label = "Your answer",
                    interactive=True
                )

                final_submit_btn = gr.Button("Submit final chase answer")

                final_feedback_md = gr.Markdown("Final chase feedback will appear here")
                final_progress_md = gr.Markdown("Final chase progress: 0 correct")

        # ---------- Footer / debug ----------
        gr.Markdown(
            "-----\n"
            "_Debug info and advanced controls may be added here later._"
        )

        # ---------- Callbacks ----------

        def start_new_game_cb(root_dir_str: str):
            root_dir_path = pathlib.Path(root_dir_str)

            # 1) Initialize game state (loads questions + starts Cash Builder)
            state: GameState = initialize_game(root_dir_path)

            # 2) Create ChaserLogic with the chosen persona for this game
            persona = state.persona
            persona_name = persona.name if persona else "Unknown chaser"
            chaser = ChaserLogic(
                model="gpt-4.1-mini",
                p_correct=0.75,
                persona=persona,
            )

            # 3) Top-level status texts
            phase_text = f"**Phase:** {state.phase.name}"
            persona_text = f"**Chaser persona:** {persona_name}"
            secured_text = f"**Secured cash:** {state.player.secured_cash}"

            # 4) First Cash Builder question
            q = get_cash_builder_question(state)
            if q is not None:
                cb_q_md = (
                    f"**Question:** {q.question}\n\n"
                    f"A) {q.options['A']}\n"
                    f"B) {q.options['B']}\n"
                    f"C) {q.options['C']}\n"
                    f"D) {q.options['D']}"
                )
            else:
                cb_q_md = "No Cash Builder questions available."

            cb_feedback = "Answer the question to begin."
            cb_progress = f"Correct answers: {state.player.correct_answers}"

            # 5) Reset Chase tab display to initial placeholders
            board_status = "Board: Player at –, Chaser at –"
            chase_q_md = "Question will appear here."
            chaser_choice_text = "**Chaser choice:** –"
            chaser_correct_text = "**Chaser correct?:** –"
            chaser_comment_text = "_Chaser comment will appear here._"
            chase_status_text = "Chase status will appear here."

            return (
                state,                 # game_state
                chaser,                # chaser_logic_state
                phase_text,            # current_phase_md
                persona_text,          # current_persona_md
                secured_text,          # secured_cash_md
                cb_q_md,               # cash_builder_question_md
                cb_feedback,           # cash_builder_feedback_md
                cb_progress,           # cash_builder_progress_md
                board_status,          # board_status_md
                chase_q_md,            # chase_question_md
                chaser_choice_text,    # chaser_choice_md
                chaser_correct_text,   # chaser_correct_md
                chaser_comment_text,   # chaser_comment_md
                chase_status_text,     # chase_status_md
            )

        start_new_game_btn.click(
            start_new_game_cb,
            inputs=[root_dir_state],
            outputs=[
                game_state,
                chaser_logic_state,
                current_phase_md,
                current_persona_md,
                secured_cash_md,
                cash_builder_question_md,
                cash_builder_feedback_md,
                cash_builder_progress_md,
                board_status_md,
                chase_question_md,
                chaser_choice_md,
                chaser_correct_md,
                chaser_comment_md,
                chase_status_md,
            ],
        )

        def cash_builder_submit_cb(
            state: GameState,
            chaser_logic: ChaserLogic,
            player_choice: str,
        ):
            """
            Handle a Cash Builder answer.
            """
            if state is None:
                return (
                    state,
                    "Game not started.",
                    "Correct answers: 0",
                    "**Phase:** –",
                    "**Chaser persona:** –",
                    "**Secured cash:** 0",
                    "No question available.",
                )

            # If player didn't pick A/B/C/D, treat as incorrect
            if player_choice not in ["A", "B", "C", "D"]:
                player_choice = "X"

            # Process answer
            before_points = state.player.correct_answers
            state = advence_cash_builder(state, player_choice)
            after_points = state.player.correct_answers
            gained = after_points - before_points

            # Feedback
            if gained == 1:
                feedback = "Correct!"
            else:
                feedback = "Wrong."

            progress_text = f"Correct answers: {state.player.correct_answers}"
            phase_text = f"**Phase:** {state.phase.name}"
            persona_text = f"**Chaser persona:** {state.persona.name}"
            secured_text = f"**Secured cash:** {state.player.secured_cash}"

            # If still in Cash Builder → show next question
            if state.phase == GamePhase.CASH_BUILDER:
                q = get_cash_builder_question(state)
                if q is not None:
                    q_md = (
                        f"**Question:** {q.question}\n\n"
                        f"A) {q.options['A']}\n"
                        f"B) {q.options['B']}\n"
                        f"C) {q.options['C']}\n"
                        f"D) {q.options['D']}"
                    )
                else:
                    q_md = "No more questions."
                return (
                    state,
                    feedback,
                    progress_text,
                    phase_text,
                    persona_text,
                    secured_text,
                    q_md,
                )

            # If Cash Builder finished → show CHASE offers
            if state.phase == GamePhase.CHASE:
                offers = prepare_chase_offers(state)

                offers_md = (
                    f"### Cash Builder complete!\n\n"
                    f"Your base cash: {state.player.correct_answers * 1000}\n\n"
                    f"**Choose your offer:**\n"
                    f"- **Low:** {offers.low_offer_money} (start pos {offers.low_start_pos})\n"
                    f"- **Middle:** {offers.mid_offer_money} (start pos {offers.mid_start_pos})\n"
                    f"- **High:** {offers.high_offer_money} (start pos {offers.high_start_pos})\n"
                    "\n"
                    "_Offer selection will be implemented in the next step._"
                )

                return (
                    state,
                    feedback,
                    progress_text,
                    phase_text,
                    persona_text,
                    secured_text,
                    offers_md,
                )

            # Otherwise (should not happen)
            return (
                state,
                feedback,
                progress_text,
                phase_text,
                persona_text,
                secured_text,
                "Unexpected state.",
            )

        cash_builder_submit_btn.click(
            cash_builder_submit_cb,
            inputs=[game_state, chaser_logic_state, cash_builder_options],
            outputs=[
                game_state,
                cash_builder_feedback_md,
                cash_builder_progress_md,
                current_phase_md,
                current_persona_md,
                secured_cash_md,
                cash_builder_question_md,
            ],
        )

        def choose_offer_cb(state: GameState, choice: str):
            if state is None:
                return(
                    state,
                    "**Phase:** -",
                    "**Secured cash:** 0",
                    "No game in progress",
                    "No chase question",
                    "No offer selected"
                )
            
            if state.phase != GamePhase.CHASE:
                return (
                    state,
                    f"**Phase:** {state.phase.name}",
                    f"**Secured cash:** {state.player.secured_cash}",
                    "Board: Offer selection is only available after cash builder",
                    "No chase question yet",
                    "You can only choose an offer after cash builder is finished"
                )
            
            choice = (choice or "").strip().lower()
            if choice not in ["low", "mid", "high"]:
                feedback = "Please select an offer before confirming"
                return(
                    state,
                    f"**Phase:** {state.phase.name}",
                    f"Secured cash:** {state.player.secured_cash}",
                    "Board: Offer not chosen",
                    "No chase question yet",
                    feedback
                )
            
            offers = prepare_chase_offers(state)
            state = choose_chase_offer(state, offers, choice)

            q = get_next_chase_question_for_state(state)
            if q is not None:
                chase_q_md = (
                    f"**Question:** {q.question}\n\n"
                    f"A) {q.options['A']}\n"
                    f"B) {q.options['B']}\n"
                    f"C) {q.options['C']}\n"
                    f"D) {q.options['D']}"
                )
            
            else:
                chase_q_md = "No chase question available"

            board_status = (
                f"Board: Player at {state.player.board_position}, "
                f"Chaser at {state.chaser.board_position}"
            )

            phase_text = f"**Phase:** {state.phase.name}"
            secured_text = f"**Secured cash:** {state.player.secured_cash}"

            cb_feedback = (
                f"Offer selected: **{choice}** "
                f"({state.offers.chosen_offer_money}) "
                "Switch to the **Chase** tab to continue"
            )

            return (
                state,
                phase_text,
                secured_text,
                board_status,
                chase_q_md,
                cb_feedback
            )
        
        offer_confirm_btn.click(
            choose_offer_cb,
            inputs=[game_state, offer_choice_radio],
            outputs=[
                game_state,
                current_phase_md,
                secured_cash_md,
                board_status_md,
                chase_question_md,
                cash_builder_feedback_md
            ],
        )

        def chase_submit_cb(state: GameState, chaser_logic: ChaserLogic, player_choice: str):
            if state is None or chaser_logic is None:
                return(
                    state,
                    "**Phase:** -",
                    "**Secured cash:** 0",
                    "Board: No active game",
                    "No chase question",
                    "**Chaser choice:** -",
                    "**Chaser correct?:** -",
                    "No comment",
                    "Start a new game first"
                )
            
            if state.phase != GamePhase.CHASE:
                return(
                    state,
                    f"**Phase:** {state.phase.name}",
                    f"**Secured cash:** {state.player.secured_cash}",
                    "Board: Not in chase phase",
                    "No chase question",
                    "**Chaser choice:** -",
                    "**Chaser correct?:** -",
                    "No comment",
                    "You can only answer Chase questions during the chase phase"
                )
            
            if player_choice not in ["A", "B", "C", "D"]:
                player_choice = "X"

            if state.current_question is None:
                q = get_next_chase_question_for_state(state)
                state.current_question = q

            state, chaser_answer, comment = run_chase_step_with_chaser(state, player_choice, chaser_logic)

            board_status = (
                f"Board: Player at {state.player.board_position}, "
                f"Chaser at {state.chaser.board_position}"
            )

            chaser_choice_text = f"**Chaser choice:** {chaser_answer.chosen_option}"
            chaser_correct_text = "**Chaser correct?:** yes" if chaser_answer.is_correct else "**Chaser correct?:** no"

            chaser_comment_text = comment

            phase_text = f"**Phase:** {state.phase.name}"
            secured_text = f"**Secured cash:** {state.player.secured_cash}"

            if state.phase == GamePhase.CHASE:
                q_next = get_next_chase_question_for_state(state)
                if q_next is not None:
                    q_md = (
                        f"**Question:** {q_next.question}\n\n"
                        f"A) {q_next.options['A']}\n"
                        f"B) {q_next.options['B']}\n"
                        f"C) {q_next.options['C']}\n"
                        f"D) {q_next.options['D']}"
                    )

                else:
                    q_md = "No more chase questions"
                chase_status = "Next chase question is ready"

            else:
                if state.outcome_message:
                    chase_status = state.outcome_message
                else:
                    chase_status = f"Chase finished. Phase: {state.phase.name}"
                q_md = "Chase phase is over"

            return (
                state,
                phase_text,
                secured_text,
                board_status,
                q_md,
                chaser_choice_text,
                chaser_correct_text,
                chaser_comment_text,
                chase_status
            )
        
        chase_submit_btn.click(
                chase_submit_cb,
                inputs=[game_state, chaser_logic_state, chase_options],
                outputs=[
                    game_state,
                    current_phase_md,
                    secured_cash_md,
                    board_status_md,
                    chase_question_md,
                    chaser_choice_md,
                    chaser_correct_md,
                    chaser_comment_md,
                    chase_status_md
                ]
            )
        
        def final_start_cb(state: GameState):
            if state is None:
                return (
                    state,
                    "**Phase:** -",
                    "**Secured cash:** 0",
                    "No active game",
                    "Final chase progress: 0 correct"
                )
            
            state = start_final_chase_default(state)

            phase_text = f"**Phase:** {state.phase.name}"
            secured_text = f"**Secured cash:** {state.player.secured_cash}"

            q = get_final_chase_player_question(state)
            if q is not None:
                q_md = (
                    f"**Question:** {q.question}\n\n"
                    f"A) {q.options['A']}\n"
                    f"B) {q.options['B']}\n"
                    f"C) {q.options['C']}\n"
                    f"D) {q.options['D']}"
                )

            else:
                q_md = "No final chase question available"

            progress = "Final chase progress: 0 correct"

            return (
                state,
                phase_text,
                secured_text,
                q_md,
                progress
            )
        
        final_start_btn.click(
            final_start_cb,
            inputs=[game_state],
            outputs=[
                game_state,
                current_phase_md,
                secured_cash_md,
                final_question_md,
                final_progress_md
            ]
        )

        def final_submit_cb(state:GameState, player_choice: str):
            if state is None:
                return(
                    state,
                    "**Phase:** -",
                    "**Secured cash:** 0",
                    "No active game",
                    "Final chase progress: 0 correct"
                )
            
            if state.phase != GamePhase.FINAL_CHASE:
                return(
                    state,
                    f"**Phase:** {state.phase.name}",
                    f"**Secured cash:** {state.player.secured_cash}"
                    "Not in final chase phase",
                    "Final chase progress: 0 correct"
                )
            
            if player_choice not in ["A", "B", "C", "D"]:
                player_choice = "X"

            before_correct = state.final_chase.player_current_index if hasattr(
                state.final_chase, "player_correct"
            ) else 0

            state = advence_final_chase_player(state, player_choice)

            after_correct = state.final_chase.player_current_index if hasattr(
                state.final_chase, "player_correct"
            ) else before_correct

            gained = after_correct - before_correct
            if gained > 0:
                feedback = "Correct in final chase"
            else:
                feedback = "Wrong in final chase"

            phase_text = f"**Phase:** {state.phase.name}"
            secured_text = f"**Secured cash:** {state.player.secured_cash}"
            progress = f"Final chase progress: {after_correct} correct"

            if state.phase == GamePhase.FINAL_CHASE:
                q = get_final_chase_player_question(state)
                if q is not None:
                    q_md = (
                        f"**Question:** {q.question}\n\n"
                        f"A) {q.options['A']}\n"
                        f"B) {q.options['B']}\n"
                        f"C) {q.options['C']}\n"
                        f"D) {q.options['D']}"
                    )

                else:
                    q_md = "No more final chase questions"

                full_feedback = feedback

            else:
                if state.outcome_message:
                    full_feedback = f"{feedback}\n\n{state.outcome_message}"
                else:
                    full_feedback = f"{feedback}\n\nFinal chase finished"
                q_md = "Final chase is over"

            return(
                state,
                phase_text,
                secured_text,
                full_feedback,
                progress,
                q_md
            )
        
        final_submit_btn.click(
            final_submit_cb,
            inputs=[game_state, final_options],
            outputs=[
                game_state,
                current_phase_md,
                secured_cash_md,
                final_feedback_md,
                final_progress_md,
                final_question_md
            ]
        )

    return demo
