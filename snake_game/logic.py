from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import List, Optional, Protocol, Tuple

Point = Tuple[int, int]
Direction = Tuple[int, int]


class SupportsChoice(Protocol):
    def choice(self, seq: List[Point]) -> Point:
        ...


@dataclass(frozen=True)
class GameState:
    width: int
    height: int
    snake: List[Point]
    food: Point
    direction: Direction
    score: int = 0
    game_over: bool = False
    lives: int = 3
    max_lives: int = 3


UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)


def _initial_snake(width: int, height: int) -> List[Point]:
    center = (width // 2, height // 2)
    return [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]


def _respawn_snake(width: int, height: int, length: int, rng: Optional[SupportsChoice] = None) -> List[Point]:
    picker = rng or Random()
    # 随机选择起始位置
    start_x = picker.choice(list(range(width)))
    start_y = picker.choice(list(range(height)))
    
    # 从起始位置生成蛇身
    snake = [(start_x, start_y)]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    for _ in range(min(length - 1, width * height - 1)):
        # 尝试向任意方向延伸
        for dx, dy in picker.choice([directions]):
            next_x = snake[-1][0] + dx
            next_y = snake[-1][1] + dy
            if 0 <= next_x < width and 0 <= next_y < height and (next_x, next_y) not in snake:
                snake.append((next_x, next_y))
                break
        else:
            # 如果所有方向都不可行，尝试找任意空位
            occupied = set(snake)
            available = [(x, y) for x in range(width) for y in range(height) if (x, y) not in occupied]
            if available:
                snake.append(picker.choice(available))
            else:
                break
    
    return snake


def _direction_from_snake(snake: List[Point]) -> Direction:
    if len(snake) < 2:
        return RIGHT
    return (snake[0][0] - snake[1][0], snake[0][1] - snake[1][1])


def create_initial_state(
    width: int = 20, height: int = 20, rng: Optional[SupportsChoice] = None
) -> GameState:
    if width < 4 or height < 4:
        raise ValueError("Board must be at least 4x4.")
    snake = _initial_snake(width, height)
    food = spawn_food(snake, width, height, rng)
    return GameState(
        width=width,
        height=height,
        snake=snake,
        food=food,
        direction=RIGHT,
    )


def update_direction(current: Direction, requested: Direction) -> Direction:
    if requested == (-current[0], -current[1]):
        return current
    return requested


def spawn_food(
    snake: List[Point], width: int, height: int, rng: Optional[SupportsChoice] = None
) -> Point:
    occupied = set(snake)
    available = [
        (x, y) for y in range(height) for x in range(width) if (x, y) not in occupied
    ]
    if not available:
        raise ValueError("No space left to spawn food.")
    picker = rng or Random()
    return picker.choice(available)


def _after_collision(state: GameState, rng: Optional[SupportsChoice]) -> GameState:
    next_lives = state.lives - 1
    if next_lives <= 0:
        return GameState(
            width=state.width,
            height=state.height,
            snake=state.snake,
            food=state.food,
            direction=state.direction,
            score=state.score,
            game_over=True,
            lives=0,
            max_lives=state.max_lives,
        )
    next_snake = _respawn_snake(state.width, state.height, len(state.snake), rng)
    next_food = spawn_food(next_snake, state.width, state.height, rng)
    return GameState(
        width=state.width,
        height=state.height,
        snake=next_snake,
        food=next_food,
        direction=_direction_from_snake(next_snake),
        score=state.score,
        game_over=False,
        lives=next_lives,
        max_lives=state.max_lives,
    )


def step_state(
    state: GameState,
    requested_direction: Optional[Direction] = None,
    rng: Optional[SupportsChoice] = None,
) -> GameState:
    if state.game_over:
        return state

    direction = state.direction
    if requested_direction is not None:
        direction = update_direction(direction, requested_direction)

    head_x, head_y = state.snake[0]
    next_head = (head_x + direction[0], head_y + direction[1])

    if (
        next_head[0] < 0
        or next_head[0] >= state.width
        or next_head[1] < 0
        or next_head[1] >= state.height
    ):
        return _after_collision(
            GameState(
                width=state.width,
                height=state.height,
                snake=state.snake,
                food=state.food,
                direction=direction,
                score=state.score,
                game_over=state.game_over,
                lives=state.lives,
                max_lives=state.max_lives,
            ),
            rng,
        )

    grow = next_head == state.food
    body_for_collision = state.snake if grow else state.snake[:-1]
    if next_head in body_for_collision:
        return _after_collision(
            GameState(
                width=state.width,
                height=state.height,
                snake=state.snake,
                food=state.food,
                direction=direction,
                score=state.score,
                game_over=state.game_over,
                lives=state.lives,
                max_lives=state.max_lives,
            ),
            rng,
        )

    next_snake = [next_head] + state.snake
    next_score = state.score
    next_food = state.food

    if grow:
        next_score += 1
        if len(next_snake) == state.width * state.height:
            return GameState(
                width=state.width,
                height=state.height,
                snake=next_snake,
                food=state.food,
                direction=direction,
                score=next_score,
                game_over=True,
                lives=state.lives,
                max_lives=state.max_lives,
            )
        next_food = spawn_food(next_snake, state.width, state.height, rng)
    else:
        next_snake.pop()

    return GameState(
        width=state.width,
        height=state.height,
        snake=next_snake,
        food=next_food,
        direction=direction,
        score=next_score,
        game_over=False,
        lives=state.lives,
        max_lives=state.max_lives,
    )
