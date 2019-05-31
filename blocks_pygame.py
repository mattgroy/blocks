import pygame
import sys

from source import driver, game, utils
from source import settings as sett

cell_size = sett.cell_size
clock = pygame.time.Clock()


def disp_msg(app, msg, top_left, font):
    x, y = top_left
    for line in msg.splitlines():
        app.screen.blit(
            font.render(
                line, False, (255, 255, 255), (0, 0, 0)),
            (x, y))
        y += 18


def center_msg(app, msg, font):
    for i, line in enumerate(msg.splitlines()):
        msg_image = font.render(
            line, False, (255, 255, 255), (0, 0, 0))

        msgim_center_x, msgim_center_y = msg_image.get_size()
        msgim_center_x //= 2
        msgim_center_y //= 2

        app.screen.blit(
            msg_image,
            (app.width //
             2 -
             msgim_center_x,
             app.height //
             2 -
             msgim_center_y +
             i *
             22))


def draw_matrix(app, matrix, offset):
    off_x, off_y = offset
    for y, row in enumerate(matrix):
        for x, val in enumerate(row):
            if val:
                pygame.draw.rect(
                    app.screen,
                    sett.colors[val.color][val.curr_draw],
                    pygame.Rect(
                        off_x + x * cell_size,
                        off_y + y * cell_size,
                        cell_size - 0.5,
                        cell_size - 0.5),
                    0)


def normalize_pos(pos, app):
    x, y = pos
    # x -= app.width_st_player
    x //= cell_size
    y //= cell_size
    return x, y


def quit_game(app):
    # center_msg(app, 'Exiting...', app.score_font)
    # pygame.display.update()
    pygame.quit()
    sys.exit()


def handle_events(app):
    for event in pygame.event.get():
        if event.type is pygame.QUIT:
            quit_game(app)

        elif event.type is pygame.MOUSEMOTION:
            app.mouse_pos = event.pos
            app.highlight(*normalize_pos(event.pos, app))

        elif event.type is pygame.MOUSEBUTTONDOWN:
            app.remove_at_playerside(*normalize_pos(event.pos, app))

        elif event.type is pygame.KEYDOWN:
            for key in sett.key_actions:
                if event.key == eval('pygame.K_' + key):
                    eval(sett.key_actions[key])


# TODO: check for possible moves here
# TODO: AI moves here
def handle_logic(app):
    pass


def handle_drawing(app):
    app.screen.fill((0, 0, 0))
    if app.gameover:
        app.center_msg(
            'Game Over!\n\nYour score: {}\n\nPress SPACE button to continue'.format(
                app.score))
    else:
        # pygame.draw.line(
        #     app.screen,
        #     (255, 255, 255),
        #     (app.rlim_enemy - 2, 0),
        #     (app.rlim_enemy - 2, app.height - 1))
        #
        # pygame.draw.line(
        #     app.screen,
        #     (255, 255, 255),
        #     (app.width_st_player - sett.cell_size, 0),
        #     (app.width_st_player - sett.cell_size, app.height - 1)
        # )

        pygame.draw.line(
            app.screen,
            (255, 255, 255),
            (0, 0),
            (0, app.height - 1)
        )

        pygame.draw.line(
            app.screen,
            (255, 255, 255),
            (app.rlim_player, 0),
            (app.rlim_player, app.height - 1))

        disp_msg(
            app,
            'Blocks selected: {}'.format(
                app.highlighted),
            (app.rlim_player + cell_size, cell_size * 2),
            pygame.font.Font(*app.score_font))

        disp_msg(
            app,
            'Score per selected blocks: {}'.format(
                utils.count_score(app.highlighted)),
            (app.rlim_player + cell_size, cell_size * 3),
            pygame.font.Font(*app.score_font))

        disp_msg(
            app,
            'Score: {}'.format(app.score_player),
            (app.rlim_player + cell_size, cell_size * 5),
            pygame.font.Font(*app.score_font))

        disp_msg(
            app,
            'Mouse at {0}, {1}'.format(*app.mouse_pos),
            (app.rlim_player + cell_size, cell_size * 7),
            pygame.font.Font(*app.score_font))

        draw_matrix(app, app.field_player.map, (0, 0))

    pygame.display.update()


def run(app):
    app.screen = pygame.display.set_mode((app.width, app.height))
    while True:
        handle_events(app)
        handle_logic(app)
        handle_drawing(app)
        clock.tick(sett.max_fps)


def main():
    pygame.init()
    app = driver.Blocks(sett.cols, sett.rows, 1)
    run(app)


if __name__ == '__main__':
    main()
