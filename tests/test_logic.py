import unittest

from snake_game.logic import (
    DOWN,
    RIGHT,
    GameState,
    create_initial_state,
    step_state,
    update_direction,
)


class FixedChoice:
    def __init__(self, value):
        self.value = value

    def choice(self, _seq):
        return self.value


class TestSnakeLogic(unittest.TestCase):
    def test_default_board_is_square_20(self):
        state = create_initial_state(rng=FixedChoice((0, 0)))
        self.assertEqual(state.width, 20)
        self.assertEqual(state.height, 20)
        self.assertEqual(state.lives, 3)

    def test_reverse_direction_is_blocked(self):
        self.assertEqual(update_direction(RIGHT, (-1, 0)), RIGHT)

    def test_growth_and_score(self):
        state = GameState(
            width=10,
            height=10,
            snake=[(3, 3), (2, 3), (1, 3)],
            food=(4, 3),
            direction=RIGHT,
            score=0,
            game_over=False,
        )
        next_state = step_state(state, rng=FixedChoice((0, 0)))
        self.assertEqual(next_state.score, 1)
        self.assertEqual(len(next_state.snake), 4)
        self.assertEqual(next_state.food, (0, 0))
        self.assertFalse(next_state.game_over)

    def test_wall_collision_loses_one_life(self):
        state = GameState(
            width=5,
            height=5,
            snake=[(4, 2), (3, 2), (2, 2), (1, 2), (0, 2)],
            food=(0, 0),
            direction=RIGHT,
            score=0,
            game_over=False,
            lives=3,
        )
        next_state = step_state(state, rng=FixedChoice((0, 0)))
        self.assertFalse(next_state.game_over)
        self.assertEqual(next_state.lives, 2)
        self.assertEqual(len(next_state.snake), 5)

    def test_last_life_collision_does_not_respawn(self):
        state = GameState(
            width=5,
            height=5,
            snake=[(4, 2), (3, 2), (2, 2), (1, 2)],
            food=(0, 0),
            direction=RIGHT,
            score=0,
            game_over=False,
            lives=1,
        )
        next_state = step_state(state, rng=FixedChoice((0, 0)))
        self.assertTrue(next_state.game_over)
        self.assertEqual(next_state.lives, 0)
        self.assertEqual(len(next_state.snake), 4)

    def test_self_collision_on_last_life_ends_game(self):
        state = GameState(
            width=8,
            height=8,
            snake=[(3, 3), (3, 4), (4, 4), (4, 3)],
            food=(7, 7),
            direction=DOWN,
            score=0,
            game_over=False,
            lives=1,
        )
        next_state = step_state(state)
        self.assertTrue(next_state.game_over)
        self.assertEqual(next_state.lives, 0)


if __name__ == "__main__":
    unittest.main()
