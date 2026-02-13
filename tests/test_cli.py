import unittest

from snake_game.cli import MAX_BOARD_SIZE, MIN_BOARD_SIZE, compute_board_size


class TestCliSizing(unittest.TestCase):
    def test_compute_board_size_uses_max_square_that_fits(self):
        self.assertEqual(compute_board_size(term_rows=40, term_cols=120), 37)

    def test_compute_board_size_has_min_floor(self):
        self.assertEqual(compute_board_size(term_rows=5, term_cols=10), MIN_BOARD_SIZE)

    def test_compute_board_size_has_max_cap(self):
        self.assertEqual(compute_board_size(term_rows=200, term_cols=300), MAX_BOARD_SIZE)


if __name__ == "__main__":
    unittest.main()
