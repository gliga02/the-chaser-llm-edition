# The Chaser – LLM Edition

The Chaser – LLM Edition is an interactive quiz game inspired by the TV show *The Chase*.  
A human player competes against an LLM-powered chaser across three phases: Cash Builder, Chase, and Final Chase.

The project focuses on game logic, state management, and LLM decision-making, with a simple Gradio-based UI.

---

## Game Structure

The game consists of three phases:

### 1. Cash Builder
- The player answers a fixed number of multiple-choice questions.
- Each correct answer increases the potential prize.
- The result determines the offers in the next phase.

### 2. The Chase
- The player selects a low, middle, or high offer.
- The player and the chaser answer questions alternately.
- The chaser is powered by an LLM with one of several randomized personas.
- The game ends when the player reaches the bank or is caught by the chaser.

### 3. Final Chase
- The player answers a series of questions to build a final score.
- This version implements the player round only.
- The chaser Final Chase round can be added later.

---

## Tech Stack

- Language: Python
- UI: Gradio
- LLM: OpenAI API
- Environment management: Conda
- Data processing: Pandas
- Question dataset: OpenTriviaQA

---

## Setup

### 1. Create the environment

```bash
conda env create -f environment.yml
conda activate chaser
```

---

## Set environment variables

Create a .env file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key
```

---

## Data source

The project uses quiz questions from the <a href="https://github.com/uberspot/OpenTriviaQA">OpenTriviaQA dataset</a>.

<ul>
    <li>Raw files are stored locally in data/raw/ and are not committed.</li>
    <li>Cleaned and normalized questions are stored in data/processed/</li>
    <li>Game uses a unified question format without category or difficulty.</li>
</ul>
