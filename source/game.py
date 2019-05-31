from random import choice
from operator import itemgetter
from itertools import groupby
from source import settings as sett


class Tile:
    def __init__(self, color=None, curr_draw=0):
        self.color = color
        self.curr_draw = curr_draw

    def __str__(self):
        if self is None:
            return ' '
        return '{}'.format(sett.colors[self.color][0])


class Field:
    def __init__(self, cols, rows, curr_draw):
        self._cols = cols
        self._rows = rows
        self._curr_draw = curr_draw
        self.map = [[Tile(choice(list(sett.colors)), curr_draw)
                     for x in range(cols)] for y in range(rows)]

    def print_map(self):
        for y in range(self._rows):
            for x in range(self._cols):
                print(self.map[y][x], end=' ')
            print()

    def _print_line(self, y):
        for x in range(self._cols):
            print(self.map[y][x], end=' ')
        print()

    def _print_column(self, x):
        for y in range(self._rows):
            print(self.map[y][x])
        print()

    def _get_chain(self, y, x):
        if self.map[x][y] is None:
            return set()
        curr_color = self.map[x][y].color
        same_color_set = set()
        self._check_neighbours(x, y, curr_color, same_color_set)
        return same_color_set

    def _check_neighbours(self, y, x, color, col_set):
        # i (x) - row
        # j (y) - collumn
        col_set.add((x, y))
        for i, j in ((x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)):
            if (i, j) in col_set:
                continue
            if -1 < i < self._cols and -1 < j < self._rows:
                if self.map[j][i] is not None and self.map[j][i].color is color:
                    self._check_neighbours(j, i, color, col_set)

    def _remove_chain(self, chain):
        if len(chain) < 2:
            return

        for x, y in chain:
            self.map[y][x] = None

        for key, group in groupby(sorted(chain), itemgetter(0)):
            g = set(group)
            t = max(g, key=itemgetter(1))
            x = t[0]
            m = t[1]

            for y in range(m - 1, -1, -1):
                if self.map[y][x] is not None:
                    z = y
                    while z < self._rows - 1 and self.map[z + 1][x] is None:
                        z = z + 1
                    self.map[z][x] = Tile(
                        self.map[y][x].color, self._curr_draw)
                    self.map[y][x] = None

    # TODO: try-catch?
    def remove_at_pos(self, y, x):
        if -1 < y < self._cols and -1 < x < self._rows:
            chain = self._get_chain(y, x)
            self._remove_chain(chain)
            if chain is None:
                return 0
            return len(chain)

    def chain_at_pos(self, y, x):
        if -1 < y < self._cols and -1 < x < self._rows:
            chain = self._get_chain(y, x)
            return chain
