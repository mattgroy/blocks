from random import randrange
from operator import itemgetter
from itertools import groupby


class Tile:
    def __init__(self, color=None, light=0):
        self.color = color
        self.light = light


class Field:
    def __init__(self, cols: int, rows: int,
                 colors_num: int = 2, field: list = None):
        self._cols = cols
        self._rows = rows
        if field:
            self._map = [[Tile(t) if t is not None else None for t in line]
                         for line in field]
        else:
            self._map = [[Tile(randrange(1, colors_num + 1))
                          for x in range(cols)] for y in range(rows)]

    # def set_field(self, cols: int, rows: int, field: list):
    #     self._cols = cols
    #     self._rows = rows
    #     self._map = [[Tile(t) if t is not None else None for t in line]
    #                  for line in field]

    def cols(self):
        return self._cols

    def rows(self):
        return self._rows

    def _get_chain(self, y, x):
        if self._map[x][y] is None:
            return set()
        curr_color = self._map[x][y].color
        same_color_set = set()
        self._check_neighbours(x, y, curr_color, same_color_set)
        return same_color_set

    def _check_neighbours(self, y, x, color, col_set):
        # i (x) - row
        # j (y) - column
        col_set.add((x, y))
        for i, j in ((x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)):
            if (i, j) in col_set:
                continue
            if -1 < i < self._cols and -1 < j < self._rows:
                if self._map[j][i] is not None and self._map[j][i].color is color:
                    self._check_neighbours(j, i, color, col_set)

    def _remove_chain(self, chain):
        if len(chain) < 2:
            return
        for x, y in chain:
            self._map[y][x] = None

        # цикл опускает все элементы вниз до упора
        for key, group in groupby(sorted(chain), itemgetter(0)):
            g = set(group)
            t = max(g, key=itemgetter(1))
            x = t[0]
            m = t[1]
            for y in range(m - 1, -1, -1):
                if self._map[y][x] is not None:
                    z = y
                    while z < self._rows - 1 and self._map[z + 1][x] is None:
                        z = z + 1
                    self._map[z][x] = Tile(
                        self._map[y][x].color)
                    self._map[y][x] = None

        self._combine_columns()

    def _combine_columns(self):
        for i, tile in enumerate(self._map[-1]):
            if not tile:
                if i + 1 == self._cols:
                    continue
                offset = 0
                start = 0
                for j, t in enumerate(self._map[-1][i + 1:]):
                    if t:
                        start = j + i + 1
                        offset = j + 1
                        break
                if offset > 0:
                    for col in range(start, self._cols):
                        for row in range(self._rows):
                            self._map[row][col - offset] = self._map[row][col]
                            self._map[row][col] = None

    # TODO: try-catch?
    def remove_at_pos(self, y: int, x: int):
        if -1 < y < self._cols and -1 < x < self._rows:
            chain = self._get_chain(y, x)
            self._remove_chain(chain)
            if chain is None:
                return 0
            return len(chain)

    def chain_at_pos(self, y: int, x: int):
        if -1 < y < self._cols and -1 < x < self._rows:
            chain = self._get_chain(y, x)
            return chain

    def highlight(self, chain):
        if len(chain) > 1:
            for i, j in chain:
                self._map[j][i].light = 1

    def dehighlight(self, chain):
        for i, j in chain:
            if self.map()[j][i]:
                self.map()[j][i].light = 0

    def is_any_posible_move(self):
        for row in range(self._rows - 1, -1, -1):
            for col, tile in enumerate(self._map[row]):
                if len(self._get_chain(col, row)) > 1:
                    return True
        return False

    def map(self):
        return self._map
