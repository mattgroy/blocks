import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
import src.blocks as bl


name = 'Player'
field = [
    [2, 1, 1, 3, 2],
    [1, 1, 0, 3, 4],
    [2, 1, 1, 3, 0],
    [4, 0, 0, 3, 0]
]


def test_start_random():
    game = bl.Blocks(30, 29, 5, name)
    game.start_new_game()
    assert game.cols() == 30
    assert game.rows() == 29
    assert game.colors_num() == 5
    assert game.name() == name
    assert game.field() is not None
    assert game.score() == 0
    assert game.highlighted() == 0
    assert game.gameover() is False


def test_set_field_and_remove_till_gameover():
    game = bl.Blocks()
    game.set_field(5, 4, field)
    assert game.field().map()[3][4].color == 0
    game.remove_at(1, 2)
    assert game.field().map()[2][2].color == 0
    game.remove_at(3, 1)
    assert game.field().map()[2][3].color == 0
    assert game.field().map()[1][3].color == 4
    game.remove_at(3, 2)
    assert game.field().map()[2][2] is None
    assert game.field().map()[2][1].color == 2
    assert game.field().map()[3][1].color == 4
    game.remove_at(0, 3)
    game.remove_at(0, 4)
    assert game.field().map()[3][0].color == 2
    game.remove_at(0, 3)
    assert game.gameover() is True
    assert game.score() == 88
    game.start_again()
    assert game.gameover() is False
    assert game.field().map()[2][3].color == 3


def test_highlight():
    game = bl.Blocks()
    game.set_field(5, 4, field)
    game.highlight(1, 2)
    assert game.field().map()[1][0].light == 1
    assert game.field().map()[0][1].light == 1
    assert game.field().map()[1][1].light == 1
    assert game.field().map()[2][1].light == 1
    assert game.field().map()[0][2].light == 1
    assert game.field().map()[2][2].light == 1
    assert game.highlighted() == 6
    assert game.count_score(6) == 6**2
    game.highlight(3, 3)
    assert game.field().map()[2][1].light == 0
    assert game.field().map()[0][3].light == 1


# REMOVED FROM src.blocks - processes are now created and held in main app file
# For multiprocessing
# def test_count_highest():
#     game = bl.Blocks()
#     game.set_field(5, 4, field)
#     i = 3
#     highest = [bl.count_highest_score(game, 2) for _ in range(i)]
#     assert highest == [88 for _ in range(i)]


def test_change_settings():
    game = bl.Blocks(10, 10, 5)
    game.change_settings(8, 7, 3, 'Changed')
    assert game.rows() == 7
    assert game.cols() == 8
    assert game.colors_num() == 3
    assert game.name() == 'Changed'


if __name__ == '__main__':
    pytest.main()
