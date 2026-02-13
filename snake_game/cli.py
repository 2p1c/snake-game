from __future__ import annotations

import curses
import locale
import os
import random
import sys
import time
from typing import Dict, List, Tuple

from snake_game.logic import DOWN, LEFT, RIGHT, UP, GameState, create_initial_state, step_state
try:
    import pyfiglet
except ImportError:  # optional dependency
    pyfiglet = None

CELL_WIDTH = 3
MIN_BOARD_SIZE = 4
MAX_BOARD_SIZE = 48
WALL_GLYPH = "\uf268"

NPC_PLAYERS = [
    ("\ueb6a", "Gemini"),
    ("\U000f0b79", "OpenAI"),
    ("\ue606", "Python"),
    ("\uf1b0", "Claude"),
    ("\uf31b", "Linux"),
]
GITHUB_ICON = "\uea84"
MEDALS = ["🥇", "🥈", "🥉"]

KEYS: Dict[int, tuple[int, int]] = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
}


def _safe_addch(stdscr: curses.window, y: int, x: int, ch: str) -> None:
    try:
        stdscr.addch(y, x, ch)
    except curses.error:
        pass


def _safe_addstr(stdscr: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def get_wall_glyph() -> str:
    encoding = (sys.stdout.encoding or locale.getpreferredencoding(False) or "").lower()
    return WALL_GLYPH if "utf" in encoding else "###"


def _draw_wall_cell(stdscr: curses.window, y: int, x: int, glyph: str, attr: int = 0) -> None:
    if glyph == "###":
        try:
            stdscr.addstr(y, x, "###", attr)
        except curses.error:
            pass
        return
    try:
        stdscr.addstr(y, x, glyph, attr)
    except curses.error:
        try:
            stdscr.addstr(y, x, "###", attr)
        except curses.error:
            pass


def speed_delay(score: int) -> float:
    return max(0.01, 0.16 - score * 0.005)


def compute_board_size(term_rows: int, term_cols: int) -> int:
    usable_rows = max(term_rows - 3, 0)
    usable_cols = max(term_cols - 2, 0) // CELL_WIDTH
    size = min(usable_rows, usable_cols, MAX_BOARD_SIZE)
    return max(MIN_BOARD_SIZE, size)


def draw_leaderboard(stdscr: curses.window, npc_scores: List[Tuple[str, str, int]], player_score: int, offset_y: int, color_enabled: bool) -> None:
    title_attr = (curses.color_pair(6) | curses.A_BOLD) if color_enabled else curses.A_BOLD
    score_attr = curses.color_pair(5) if color_enabled else 0
    player_attr = (curses.color_pair(1) | curses.A_BOLD) if color_enabled else curses.A_BOLD
    
    _safe_addstr(stdscr, offset_y, 2, "🏆 TOP SCORES", title_attr)
    
    # 合并GitHub玩家和NPC分数
    all_scores = [(GITHUB_ICON, "GitHub", player_score)] + npc_scores
    all_scores.sort(key=lambda x: x[2], reverse=True)
    
    for idx, (icon, name, score) in enumerate(all_scores[:10]):
        medal = MEDALS[idx] if idx < 3 else " "
        is_player = (name == "GitHub")
        attr = player_attr if is_player else score_attr
        line = f"{medal} {icon} {score:3d}"
        _safe_addstr(stdscr, offset_y + 2 + idx, 2, line, attr)


def draw_lives(stdscr: curses.window, lives: int, max_x: int, max_y: int, offset_y: int, color_enabled: bool) -> None:
    heart = "❤️"
    heart_attr = (curses.color_pair(3) | curses.A_BOLD) if color_enabled else 0
    start_x = max_x - 4
    if start_x < 0:
        return
    for heart_idx in range(max(0, lives)):
        y_pos = offset_y + 1 + heart_idx * 2
        if y_pos < max_y:
            _safe_addstr(stdscr, y_pos, start_x, heart, heart_attr)


def draw_start_screen(stdscr: curses.window, color_enabled: bool) -> None:
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    title_attr = (curses.color_pair(1) | curses.A_BOLD) if color_enabled else curses.A_BOLD
    text_attr = curses.color_pair(5) if color_enabled else 0
    title = "PIXEL SNAKE"
    subtitle = "Press SPACE to start"
    controls = "Arrow Keys: Move   P:Pause   R:Restart   Q:Quit"
    _safe_addstr(stdscr, max(0, max_y // 2 - 2), max(0, (max_x - len(title)) // 2), title, title_attr)
    _safe_addstr(
        stdscr,
        max(0, max_y // 2),
        max(0, (max_x - len(subtitle)) // 2),
        subtitle,
        text_attr,
    )
    _safe_addstr(
        stdscr,
        max(0, max_y // 2 + 2),
        max(0, (max_x - len(controls)) // 2),
        controls,
        text_attr,
    )
    stdscr.refresh()


def create_state_for_terminal(stdscr: curses.window) -> GameState:
    max_y, max_x = stdscr.getmaxyx()
    board_size = compute_board_size(max_y, max_x)
    return create_initial_state(width=board_size, height=board_size)


def draw_game_over_banner(
    stdscr: curses.window, max_y: int, max_x: int, color_enabled: bool
) -> None:
    if pyfiglet is not None:
        banner = [
            line
            for line in pyfiglet.figlet_format("GAME OVER", font="big").splitlines()
            if line.strip()
        ]
    else:
        banner = [
            " ####   ###  #   # ####    ###  #   # ##### #### ",
            "#      #   # ## ## #      #   # #   # #     #   #",
            "# ###  ##### # # # ###    #   # #   # ###   #### ",
            "#   #  #   # #   # #      #   #  # #  #     #  # ",
            " ####  #   # #   # ####    ###    #   ##### #   #",
        ]
    attr = (curses.color_pair(2) | curses.A_BOLD) if color_enabled else curses.A_BOLD
    start_row = max(0, (max_y - len(banner)) // 2)
    for idx, line in enumerate(banner):
        x = max(0, (max_x - len(line)) // 2)
        _safe_addstr(stdscr, start_row + idx, x, line, attr)


def draw(stdscr: curses.window, state: GameState, paused: bool, color_enabled: bool, npc_scores: List[Tuple[str, str, int]]) -> bool:
    stdscr.erase()
    board_width = state.width * CELL_WIDTH + 2
    board_height = state.height + 2
    max_y, max_x = stdscr.getmaxyx()

    # 计算居中偏移
    offset_y = max(0, (max_y - board_height - 2) // 2)
    offset_x = max(0, (max_x - board_width) // 2)

    draw_leaderboard(stdscr, npc_scores, state.score, offset_y, color_enabled)
    draw_lives(stdscr, state.lives, max_x, max_y, offset_y, color_enabled)

    wall_glyph = get_wall_glyph()
    wall_attr = curses.color_pair(5) if color_enabled else 0
    text_attr = curses.color_pair(5) if color_enabled else 0
    for x in range(0, board_width, CELL_WIDTH):
        _draw_wall_cell(stdscr, offset_y, offset_x + x, wall_glyph, wall_attr)
        _draw_wall_cell(stdscr, offset_y + board_height - 1, offset_x + x, wall_glyph, wall_attr)
    for y in range(1, board_height - 1):
        _draw_wall_cell(stdscr, offset_y + y, offset_x, wall_glyph, wall_attr)
        _draw_wall_cell(stdscr, offset_y + y, offset_x + board_width - CELL_WIDTH, wall_glyph, wall_attr)

    food_x, food_y = state.food
    food_attr = (curses.color_pair(3) | curses.A_BOLD) if color_enabled else 0
    _safe_addstr(stdscr, offset_y + food_y + 1, offset_x + 1 + food_x * CELL_WIDTH, "🍎", food_attr)

    for idx, (x, y) in enumerate(state.snake):
        ch = "😮" if idx == 0 else "😳"
        color = (
            (curses.color_pair(1) | curses.A_BOLD)
            if idx == 0
            else curses.color_pair(2)
        ) if color_enabled else 0
        _safe_addstr(stdscr, offset_y + y + 1, offset_x + 1 + x * CELL_WIDTH, ch, color)

    _safe_addstr(
        stdscr,
        offset_y + board_height,
        offset_x,
        f"Score: {state.score}   P:Pause  R:Restart  Q:Quit",
        text_attr,
    )
    if paused and not state.game_over:
        _safe_addstr(stdscr, offset_y + board_height + 1, offset_x, "Paused", text_attr)
    if state.game_over:
        draw_game_over_banner(stdscr, max_y, max_x, color_enabled)
        _safe_addstr(
            stdscr,
            offset_y + board_height + 1,
            offset_x,
            "Game Over! Press R to restart or Q to quit.",
            text_attr,
        )
    stdscr.refresh()
    return max_y >= 2 and max_x >= 2


def _run(stdscr: curses.window) -> None:
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    color_enabled = False
    if curses.has_colors():
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            color_enabled = True
        except curses.error:
            color_enabled = False

    stdscr.nodelay(True)
    state = create_state_for_terminal(stdscr)
    started = False
    paused = False
    requested_direction = None
    last_tick = time.monotonic()
    
    # 为每个NPC生成20-30之间的随机分数
    npc_scores = [(icon, name, random.randint(20, 30)) for icon, name in NPC_PLAYERS]

    while True:
        target_size = compute_board_size(*stdscr.getmaxyx())
        if target_size != state.width:
            state = create_initial_state(width=target_size, height=target_size)
            paused = False
            requested_direction = None
            last_tick = time.monotonic()

        if not started:
            draw_start_screen(stdscr, color_enabled)
            key = stdscr.getch()
            if key in (ord("q"), ord("Q")):
                break
            if key == ord(" "):
                started = True
                state = create_state_for_terminal(stdscr)
                paused = False
                requested_direction = None
                last_tick = time.monotonic()
            time.sleep(0.01)
            continue

        can_render = draw(stdscr, state, paused, color_enabled, npc_scores)
        key = stdscr.getch()

        if key in KEYS and not state.game_over:
            requested_direction = KEYS[key]
        elif key in (ord("q"), ord("Q")):
            break
        elif key in (ord("p"), ord("P")) and not state.game_over:
            paused = not paused
        elif key in (ord("r"), ord("R")):
            state = create_state_for_terminal(stdscr)
            paused = False
            requested_direction = None
            last_tick = time.monotonic()
            npc_scores = [(icon, name, random.randint(20, 30)) for icon, name in NPC_PLAYERS]
            continue

        delay = speed_delay(state.score)
        if can_render and not paused and not state.game_over and (time.monotonic() - last_tick) >= delay:
            state = step_state(state, requested_direction)
            requested_direction = None
            last_tick = time.monotonic()

        time.sleep(0.01)


def run_game() -> None:
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("This game requires an interactive terminal (TTY).")
        return
    if not os.environ.get("TERM"):
        print("TERM is not set. Please run in a standard terminal.")
        return
    try:
        curses.wrapper(_run)
    except curses.error as exc:
        print(f"Terminal does not fully support curses: {exc}")
