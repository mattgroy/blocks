import sys
import PyQt5.QtWidgets as qw
from PyQt5.QtCore import QBasicTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from copy import deepcopy
from collections import deque
from operator import itemgetter
from concurrent.futures import ProcessPoolExecutor
from src.blocks import Blocks, BlocksStatSaver, count_highest


class Canvas(qw.QWidget):
    def __init__(self, game: Blocks, size: int, parent=None):
        qw.QWidget.__init__(self, parent)
        self.size = size
        self.setMouseTracking(True)
        self.colors = {
            # red
            1: ((220, 10, 20), (220, 80, 90)),
            # blue
            2: ((20, 10, 220), (90, 80, 220)),
            # green
            3: ((10, 220, 20), (80, 220, 90)),
            # purple
            4: ((120, 10, 220), (150, 70, 220)),
            # yellow
            5: ((220, 220, 10), (220, 220, 80))
        }
        self.game = game

    def mouseMoveEvent(self, e):
        x = e.x() // self.size
        y = e.y() // self.size
        self.game.highlight(x, y)

    def mousePressEvent(self, e):
        x = e.x() // self.size
        y = e.y() // self.size
        self.game.remove_at(x, y)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        for y, row in enumerate(self.game.field().map()):
            for x, val in enumerate(row):
                if val:
                    asd = self.colors[val.color][val.light]
                    qp.setBrush(QColor(*asd))
                    qp.drawRect(
                        x * self.size,
                        y * self.size,
                        self.size - 0.5,
                        self.size - 0.5)


class App(qw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.block_size = 30

        # одна из фич
        self.saved_games = deque(maxlen=3)

        self.timer = QBasicTimer()
        self.status_bar = self.statusBar()

        self.cols = 15
        self.rows = 15
        self.colors_num = 5
        self.name = 'Player'
        self._default_name = True

        self.setWindowTitle('Blocks')
        # статистика
        self.last_stats = ('You', self.cols, self.rows, 0)
        self.game = Blocks(self.cols, self.rows, self.colors_num, self.name)
        self.game.start_new_game()

        self.editor = Editor()
        self.editor.butt_ok.clicked.connect(self.edit_settings_close_editor)

        self.sl_menu = None
        self.score_table = None
        self.highest = CountHighest(self.game, 2)

        new_act = qw.QAction('&New Game', self)
        new_act.setStatusTip('Start new game')
        new_act.triggered.connect(self.start_new_game)
        again_act = qw.QAction('&Play Again', self)
        again_act.setStatusTip('Start new game with the same field')
        again_act.triggered.connect(self.start_again)
        score_act = qw.QAction('&Score Table', self)
        score_act.setStatusTip('Show score table')
        score_act.setShortcut('Ctrl+T')
        score_act.triggered.connect(self.open_score_table)
        exit_act = qw.QAction('&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(sys.exit)

        edit_act = qw.QAction('&Edit Settings', self)
        edit_act.setShortcut('Ctrl+E')
        edit_act.setStatusTip('Change nickname and field size')
        edit_act.triggered.connect(self.open_editor)

        save_act = qw.QAction('&Save', self)
        save_act.setShortcut('Ctrl+S')
        save_act.triggered.connect(lambda: self.status_bar.showMessage(
            self.save_game()))
        load_act = qw.QAction('&Load', self)
        load_act.setShortcut('Ctrl+L')
        load_act.triggered.connect(self.open_loader)

        count_act = qw.QAction('&Count Highest Score', self)
        count_act.setStatusTip('It is a long process, '
                               'some game features will be unavailable')
        count_act.triggered.connect(self.count_highest)
        cancel_act = qw.QAction('&Cancel Counting', self)
        cancel_act.triggered.connect(lambda: self.stop_counting())

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&Game')
        file_menu.addAction(new_act)
        file_menu.addAction(again_act)
        file_menu.addAction(score_act)
        file_menu.addAction(exit_act)
        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(edit_act)
        save_menu = menubar.addMenu('&Save/Load')
        save_menu.addAction(save_act)
        save_menu.addAction(load_act)
        other_menu = menubar.addMenu('&Other')
        other_menu.addAction(count_act)
        other_menu.addAction(cancel_act)

        self.acts_to_lock = (count_act, )

        self.canvas = Canvas(self.game, self.block_size, self)

        self.score_total = qw.QLCDNumber(self)
        self.score_total.display(self.game.score())
        self.score_total.setSegmentStyle(qw.QLCDNumber.Flat)
        self.score_total.setStyleSheet("""color: black; background: white;""")
        self.score_curr = qw.QLCDNumber(self)
        self.score_curr.display(Blocks.count_score(self.game.highlighted()))
        self.score_curr.setSegmentStyle(qw.QLCDNumber.Flat)
        self.score_curr.setStyleSheet("""color: black; background: white;""")
        scores_layout = qw.QHBoxLayout()
        scores_layout.addWidget(self.score_total)
        scores_layout.addWidget(self.score_curr)

        self.main_layout = qw.QVBoxLayout()
        self.main_layout.addWidget(self.canvas)
        self.main_layout.addLayout(scores_layout)

        self.centr_wid = qw.QWidget(self)
        self.centr_wid.setLayout(self.main_layout)
        self.setCentralWidget(self.centr_wid)

        self.resize_window()
        self.show()
        self.timer.start(40, self)

    def open_loader(self):
        saves = [save for save in self.saved_games]
        if saves:
            self.sl_menu = SaveLoadMenu(saves)
            [self._set_button_clicked(slot) for slot in self.sl_menu.slots]
            self.sl_menu.show()

    def _set_button_clicked(self, slot):
        slot[0].clicked.connect(lambda: self._load_game(slot[1]))

    def _load_game(self, game: Blocks):
        self.timer.stop()
        self.stop_counting()
        g = deepcopy(game)
        self.game = g
        self.canvas.game = g
        self.resize_window()
        self.timer.start(40, self)
        self.sl_menu.hide()

    def save_game(self):
        self.saved_games.append(deepcopy(self.game))
        return 'Game saved'

    def edit_settings_close_editor(self):
        self.timer.stop()
        self.stop_counting()
        settings = self.editor.get_info()
        self.editor.hide()
        self.cols, self.rows, self.colors_num = settings
        self.game.change_settings(*settings)
        self.start_new_game()
        self.setWindowTitle('Blocks ({})'.format(self.name))

    def open_editor(self):
        self.editor.pass_info(
            self.cols,
            self.rows,
            self.colors_num)
        self.editor.show()

    def open_score_table(self):
        self.score_table = ScoreTable(self.last_stats)
        self.score_table.show()

    def count_highest(self):
        self.highest = CountHighest(self.game, 2)
        self.highest.fin.connect(self.show_highest)
        [act.setDisabled(True) for act in self.acts_to_lock]
        self.highest.start()

    def show_highest(self, highest: int):
        self.stop_counting()
        self.status_bar.showMessage(
            'Possible highest score: {}'.format(highest))

    def stop_counting(self):
        self.highest.shutdown()
        [act.setDisabled(False) for act in self.acts_to_lock]

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.update_ui()
            if self.game.gameover() is True:
                self.on_gameover()
        else:
            super(App.self).timerEvent(self, event)

    def update_ui(self):
        self.score_total.display(self.game.score())
        self.score_total.update()
        self.score_curr.display(Blocks.count_score(self.game.highlighted()))
        self.score_curr.update()
        self.canvas.update()

    def on_gameover(self):
        self.timer.stop()

        if self._default_name:
            text, ok = qw.QInputDialog.getText(
                self, 'Blocks',
                'Enter your name:', text='Player')
            self.name = text or 'Player' if ok else 'Player'
            self._default_name = False
            self.game.change_settings(
                self.game.cols(),
                self.game.rows(),
                self.game.colors_num(),
                self.name)

        self.last_stats = (
            self.game.name(),
            self.game.cols(),
            self.game.rows(),
            self.game.score())
        BlocksStatSaver.save_to_stats(self.game)
        choice = qw.QMessageBox.question(
            self, 'Game Over! (Score: {})'.format(self.game.score()),
            "Do you want to start a new game?",
            qw.QMessageBox.Yes | qw.QMessageBox.Reset | qw.QMessageBox.No)
        if choice == qw.QMessageBox.Yes:
            self.start_new_game()
        elif choice == qw.QMessageBox.Reset:
            self.start_again()
        else:
            sys.exit()

    def start_new_game(self):
        self.stop_counting()
        self.game.start_new_game()
        self.resize_window()
        self.timer.start(40, self)

    def start_again(self):
        self.stop_counting()
        self.game.start_again()
        self.resize_window()
        self.timer.start(40, self)

    def resize_window(self):
        self.cols = self.game.cols()
        self.rows = self.game.rows()
        self.name = self.game.name()
        self.colors_num = self.game.colors_num()
        self.canvas.setFixedSize(
            self.cols * self.block_size,
            self.rows * self.block_size)
        self.setFixedWidth(self.cols * self.block_size + 20)
        self.setFixedHeight(self.rows * self.block_size + 100)
        self.setWindowTitle('Blocks ({})'.format(self.name))


# Multiprocessing
class CountHighest(QThread):
    fin = pyqtSignal(int)

    def __init__(self, game, workers):
        QThread.__init__(self)
        self._game = game
        self._workers = workers
        self._executor = None
        self._canceled = False

    def __del__(self):
        self.wait()

    def _count_highest_score(self):
        futures = []
        results = []
        self._canceled = False
        curr_field = self._game.field()
        curr_score = self._game.score()
        with ProcessPoolExecutor(max_workers=self._workers) as self._executor:
            for _ in range(1000):
                future = self._executor.submit(
                    count_highest, curr_field, curr_score)
                futures.append(future)
            for future in futures:
                if not self._canceled:
                    results.append(future.result())
                else:
                    future.cancel()
        return results

    def run(self):
        results = self._count_highest_score()
        highest = max(results)
        self.fin.emit(highest)

    def shutdown(self):
        if self.isRunning():
            self._canceled = True
            self._executor.shutdown(False)


class Editor(qw.QWidget):
    def __init__(self):
        super(Editor, self).__init__()
        self.setWindowTitle('Settings')
        self.setFixedSize(270, 170)

        layout_cols = qw.QHBoxLayout()
        cols_label = qw.QLabel('Columns:', self)
        self._cols_area = qw.QSpinBox(self)
        self._cols_area.setMinimum(5)
        self._cols_area.setMaximum(30)
        layout_cols.addWidget(cols_label, 1)
        layout_cols.addWidget(self._cols_area, 1)

        layout_rows = qw.QHBoxLayout()
        rows_label = qw.QLabel('Rows:', self)
        self._rows_area = qw.QSpinBox(self)
        self._rows_area.setMinimum(5)
        self._rows_area.setMaximum(30)
        layout_rows.addWidget(rows_label, 1)
        layout_rows.addWidget(self._rows_area, 1)

        layout_num = qw.QHBoxLayout()
        num_label = qw.QLabel('Number of colors:', self)
        self._num_area = qw.QSpinBox(self)
        self._num_area.setMinimum(2)
        self._num_area.setMaximum(5)
        layout_num.addWidget(num_label, 1)
        layout_num.addWidget(self._num_area, 1)

        layout_butt = qw.QHBoxLayout()
        self.butt_ok = qw.QPushButton('Yes')
        butt_cancel = qw.QPushButton('Cancel')
        butt_cancel.clicked.connect(self.hide)
        layout_butt.addWidget(self.butt_ok, 1)
        layout_butt.addWidget(butt_cancel, 1)

        layout_main = qw.QVBoxLayout()
        layout_main.addLayout(layout_cols)
        layout_main.addLayout(layout_rows)
        layout_main.addLayout(layout_num)
        layout_main.addLayout(layout_butt)

        self.setLayout(layout_main)

    def pass_info(self, cols: int, rows: int, num: int):
        self._cols_area.setValue(cols)
        self._rows_area.setValue(rows)
        self._num_area.setValue(num)

    def get_info(self):
        return self._cols_area.value(), \
            self._rows_area.value(), \
            self._num_area.value()


class SaveLoadMenu(qw.QWidget):
    def __init__(self, saves):
        super(SaveLoadMenu, self).__init__()
        self.setFixedSize(300, 0)
        self.setWindowTitle('Load')
        self._label = qw.QLabel('Choose your save:')

        self.slots = []
        for save in saves:
            self.slots.append((
                qw.QPushButton(BlocksStatSaver.get_stat_str(save)),
                save))

        layout_main = qw.QVBoxLayout()
        layout_main.addWidget(self._label)
        [layout_main.addWidget(x[0]) for x in self.slots]
        self.setLayout(layout_main)


class ScoreTable(qw.QWidget):
    def __init__(self, last):
        super(ScoreTable, self).__init__()
        self.setWindowTitle('Score Table')
        self.setFixedSize(350, 0)

        stats = sorted(
            BlocksStatSaver.get_stats(),
            key=itemgetter(3, 0),
            reverse=True)

        layout_main = qw.QGridLayout()
        layout_main.addWidget(qw.QLabel('Nickname'), 0, 0)
        layout_main.addWidget(qw.QLabel('Field Size'), 0, 1)
        layout_main.addWidget(qw.QLabel('Score'), 0, 2)
        layout_main.addWidget(self._Hline(), 1, 0, 1, 3)

        i = 2
        for stat in stats[:7]:
            layout_main.addWidget(qw.QLabel(stat[0]), i, 0)
            layout_main.addWidget(qw.QLabel('{}x{}'.format(stat[1], stat[2])),
                                  i, 1)
            layout_main.addWidget(qw.QLabel(str(stat[3])), i, 2)
            i += 1

        layout_main.addWidget(self._Hline(), i, 0, 1, 3)
        layout_main.addWidget(qw.QLabel(last[0]), i + 1, 0)
        layout_main.addWidget(qw.QLabel('{}x{}'.format(last[1], last[2])),
                              i + 1, 1)
        layout_main.addWidget(qw.QLabel(str(last[3])), i + 1, 2)
        self.setLayout(layout_main)

    def _Hline(self):
        line = qw.QFrame()
        line.setFrameShape(qw.QFrame.HLine)
        line.setFrameShadow(qw.QFrame.Sunken)
        return line

    def _Vline(self):
        line = qw.QFrame()
        line.setFrameShape(qw.QFrame.VLine)
        line.setFrameShadow(qw.QFrame.Sunken)
        return line


if __name__ == '__main__':
    app = qw.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
