# Copilot Instructions for Terminal Snake

## Build, Test, and Run Commands
- Run game: `python3 main.py`
- Run full tests: `python3 -m unittest discover -s tests -q`
- Run single test: `python3 -m unittest tests.test_logic.TestSnakeLogic.test_wall_collision -q`

## High-Level Architecture
- `main.py` is the command-line entrypoint.
- `snake_game/logic.py` contains pure state transitions and rules:
  - initial state creation
  - direction updates with reverse-direction guard
  - game step updates (movement, growth, collision, scoring)
  - food spawning
- `snake_game/cli.py` handles terminal concerns only:
  - curses initialization/color setup
  - key mapping and frame loop
  - drawing board, snake, food, score, and game-over text

## Key Conventions
- Keep logic and rendering decoupled; avoid embedding rules inside curses code.
- Keep logic deterministic and testable by injecting RNG for food placement.
- Prefer minimal dependencies; standard library first.
- Preserve day-one MVP scope: playable loop first, polish second.
- Favor fast CLI iteration:
  - run/test via direct Python commands
  - keep commands short and script-free unless needed
