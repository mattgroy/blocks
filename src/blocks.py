import re
from copy import deepcopy
from random import randrange
from src.field import Field


class Blocks:
    def __init__(self,
                 cols: int = 5,
                 rows: int = 5,
                 colors_num: int = 2,
                 name: str = 'Player'):
        self._cols = cols
        self._rows = rows
        self._colors_num = colors_num
        self._name = name
        self._field = None
        self._initial_field = None
        self._score = 0
        self._highlighted = 0
        self._highlighted_chain = None
        self._gameover = False

    def set_field(self, cols: int, rows: int, col_field: list):
        self._cols = cols
        self._rows = rows
        self._colors_num = 2
        self._initial_field = Field(
            self._cols,
            self._rows,
            field=col_field
        )
        self._field = deepcopy(self._initial_field)
        self._score = 0
        self._highlighted = 0
        self._highlighted_chain = None
        self._gameover = False

    def start_new_game(self):
        self._initial_field = Field(
            self._cols,
            self._rows,
            self._colors_num)
        self._field = deepcopy(self._initial_field)
        self._score = 0
        self._highlighted = 0
        self._highlighted_chain = None
        self._gameover = False

    def start_again(self):
        self._field = deepcopy(self._initial_field)
        self._score = 0
        self._highlighted = 0
        self._highlighted_chain = None
        self._gameover = False

    def highlight(self, y: int, x: int):
        chain = self._field.chain_at_pos(y, x)
        if chain is not self._highlighted_chain and self._highlighted_chain is not None:
                self._field.dehighlight(self._highlighted_chain)
        if chain:
            self._field.highlight(chain)
            self._highlighted_chain = chain
            self._highlighted = len(chain)

    def remove_at(self, y: int, x: int):
        self._score += self.count_score(self._field.remove_at_pos(y, x))
        if not self._field.is_any_posible_move():
            self._gameover = True

    def change_settings(self, cols: int, rows: int,
                        colors_num: int, name=None):
        self._cols = cols
        self._rows = rows
        self._colors_num = colors_num
        self._name = name if name else self._name

    # better use @property
    def cols(self):
        return self._cols

    def rows(self):
        return self._rows

    def colors_num(self):
        return self._colors_num

    def name(self):
        return self._name

    def score(self):
        return self._score

    def gameover(self):
        return self._gameover

    def field(self):
        return self._field

    def highlighted(self):
        return self._highlighted

    @staticmethod
    def count_score(num):
        if num is not None:
            num = int(num)
            if 2 < num:
                return num * num
            elif num == 2:
                return 2
            else:
                return 0
        return 0


class BlocksStatSaver:
    _filename = 'blocks_stats.txt'
    _reg = re.compile(r'(\w+)\s+\(\s*(\d+)\s*x\s*(\d+)\)\s*-\s*(\d+)')

    @staticmethod
    def save_to_stats(game: Blocks):
        stat_str = BlocksStatSaver.get_stat_str(game)
        with open(BlocksStatSaver._filename, 'a+') as f:
            f.write(stat_str + '\n')

    @staticmethod
    def get_stats():
        result = []
        open(BlocksStatSaver._filename, 'a').close()
        with open(BlocksStatSaver._filename, 'r') as f:
            for line in f:
                match = BlocksStatSaver._reg.match(line)
                if match:
                    result.append((
                        match.group(1),
                        int(match.group(2)),
                        int(match.group(3)),
                        int(match.group(4))))
        return result

    @staticmethod
    def get_stat_str(game: Blocks):
        return '{} ({}x{}) - {}'.format(
            game.name(),
            game.cols(),
            game.rows(),
            game.score())


def count_highest(curr_field, curr_score):
    field = deepcopy(curr_field)
    score = curr_score
    while field.is_any_posible_move():
        x = randrange(0, field.rows())
        y = randrange(0, field.cols())
        score += Blocks.count_score(field.remove_at_pos(y, x))
    return score
