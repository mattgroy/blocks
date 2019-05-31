import pygame
from copy import deepcopy

from source import game, utils
from source import settings as sett


class Blocks:
    def __init__(self, cols, rows, curr_draw=0):

        self._cols = cols
        self._rows = rows
        self.curr_draw = curr_draw

        self.screen = None
        self.mouse_pos = None

        # self.paused = False
        self.gameover = False

        # начало поля игрока
        # self.width_st_player = sett.cell_size * \
        #     self._cols + sett.score_width + sett.cell_size

        # границы м/у полем и результатами
        # self.rlim_enemy = sett.score_width
        self.rlim_player = sett.cell_size * self._cols
        # self.width_st_player \

        self.width = self.rlim_player + sett.score_width
        self.height = sett.cell_size * self._rows

        self.score_font = (sett.font_space, 11)

        # сделать в мэйне
        # bad idea
        # self.screen = pygame.display.set_mode((self.width, self.height))

        f = game.Field(self._cols, self._rows, self.curr_draw)
        # TODO: deepcopy?
        self.field_player = deepcopy(f)

        self.score_player = 0

        self.highlighted = 0
        self.highlighted_chain = None

        # game loop now will work at max_fps rate
        #pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
        # used to correctly implement seconds

    def init_game(self):
        f = game.Field(self._cols, self._rows, self.curr_draw)
        # TODO: deepcopy?
        self.field_player = deepcopy(f)

        self.score_player = 0

        self.highlighted = 0
        self.highlighted_chain = None

        # game loop now will work at max_fps rate
        #pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
        # used to correctly implement seconds

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    # not for console app
    def highlight(self, y, x):
        if self.highlighted_chain is not None:
            for i, j in self.highlighted_chain:
                if self.field_player.map[j][i] is not None:
                    self.field_player.map[j][i].curr_draw = self.curr_draw

        chain = self.field_player.chain_at_pos(y, x)
        if chain is not None:
            for i, j in chain:
                self.field_player.map[j][i].curr_draw = 2

            self.highlighted_chain = chain
            self.highlighted = len(chain)

    def remove_at_playerside(self, y, x):
        self.score_player += utils.count_score(
            self.field_player.remove_at_pos(y, x))
