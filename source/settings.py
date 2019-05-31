cell_size = 25
# map_size = 15
cols = 15
rows = 15
score_width = 250

max_fps = 24

font_score = 'source/assets/fonts/VarelaRound-Regular.ttf'
font_misc = 'source/assets/fonts/Pacifico-Regular.ttf'
font_space = 'source/assets/fonts/Orbitron-Regular.ttf'

# colors_console = {
#     'RED': 1,
#     'BLUE': 2,
#     'GREEN': 3,
#     'PURPLE': 4,
#     'YELLOW': 5
# }

# zero - console
# first - normal
# second - bright
colors = {
    'RED': (1, (220, 10, 20), (220, 80, 90)),
    'BLUE': (2, (20, 10, 220), (90, 80, 220)),
    'GREEN': (3, (10, 220, 20), (80, 220, 90)),
    'PURPLE': (4, (120, 10, 220), (150, 70, 220)),
    'YELLOW': (5, (220, 220, 10), (220, 220, 80))
}

key_actions = {
    'ESCAPE': 'quit_game(app)',
    # 'p': self.toggle_pause,
    'SPACE': 'app.start_game()',
    # 'RETURN':
}
