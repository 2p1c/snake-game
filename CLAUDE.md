# Terminal Snake Development Guidelines

## Goal
- Build a small, polished terminal game (ASCII/color) that can be completed in one day.
- Current selected game: **Snake (terminal color version)**.

## Tech Stack
- **Language**: Python 3
- **Rendering/Input**: `curses` (terminal UI and keyboard handling)
- **Testing**: `unittest` for pure logic

## Implementation Plan
- Start from a minimal playable loop first (move, eat, collision, game over).
- Split modules by responsibility:
  - `snake_game/logic.py`: pure game state and rules (testable, no terminal I/O)
  - `snake_game/cli.py`: terminal drawing and input loop
  - `main.py`: startup entrypoint
- Add lightweight tests around movement/collision/score behavior before polishing UI.

## Coding Conventions
- Keep game logic deterministic and side-effect light; pass RNG into logic functions when needed.
- Keep rendering separate from state transitions; UI should call logic, not embed core rules.
- Prefer simple data structures (`dataclass`, tuples, lists) over heavy abstractions.

## CLI-First Advantages to Preserve
- One-command run: `python3 main.py`
- One-command tests: `python3 -m unittest discover -s tests -q`
- Single-test run: `python3 -m unittest tests.test_logic.TestSnakeLogic.test_wall_collision -q`
- Fast iteration in terminal with no external services or build pipeline.
