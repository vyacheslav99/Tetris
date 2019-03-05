from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFrame
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

from . import engine


class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)

        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.resize(270, 570)  # 180, 380 исходный размер
        self.center()
        self.setWindowTitle('Тетрис')
        self.show()

        self.tboard.start()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


class Board(QFrame):

    msg2Statusbar = pyqtSignal(str)
    ColorTable = (0xECE9D8, 0xCC6666, 0x66CC66, 0x6666CC, 0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00)
    Speed = 1000
    BWidth = 10
    BHeight = 22

    def __init__(self, parent):
        super().__init__(parent)

        self.isStarted = False
        self.isPaused = False
        self.engine = engine.Engine(Board.BWidth, Board.BHeight)
        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        if self.isStarted:
            self.stop()

        self.engine.clear()
        self.msg2Statusbar.emit(f'Lines: {self.engine.total_lines()}')
        self.isPaused = False
        self.isStarted = True
        self.engine.start()
        self.timer.start(self.Speed, self)
        self.update()

    def stop(self):
        if not self.isStarted:
            return

        self.timer.stop()
        self.isStarted = False
        self.isPaused = False
        self.msg2Statusbar.emit(f'Game Over!   Total Lines: {self.engine.total_lines()}')
        self.update()

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit('-= PAUSED =-')
            self.update()
        else:
            self.msg2Statusbar.emit(f'Lines: {self.engine.total_lines()}')
            self.timer.start(self.Speed, self)

    def scale_width(self):
        """ масштабирование - рассчитывает размер стороны квадрата в пикселях по оси X (ширина) """
        return self.contentsRect().width() // self.BWidth

    def scale_height(self):
        """ масштабирование - рассчитывает размер стороны квадрата в пикселях по оси Y (высота) """
        return self.contentsRect().height() // self.BHeight

    def keyPressEvent(self, event):
        key = event.key()

        try:
            if key == Qt.Key_S:
                self.start()

            elif key == Qt.Key_P:
                self.pause()

            elif not self.isStarted or self.isPaused:
                return

            elif key == Qt.Key_Right:
                self.engine.move_right()

            elif key == Qt.Key_Left:
                self.engine.move_left()

            elif key == Qt.Key_Down:
                self.engine.rotate_right()

            elif key == Qt.Key_Up:
                self.engine.rotate_left()

            elif key == Qt.Key_Space:
                self.engine.drop_down()

            elif key == Qt.Key_D:
                self.engine.move_down()

            else:
                super(Board, self).keyPressEvent(event)
        except engine.StopGameException as e:
            self.stop()
        finally:
            self.update_ui()

    def timerEvent(self, event):
        try:
            if event.timerId() == self.timer.timerId():
                self.engine.move_down()
            else:
                super(Board, self).timerEvent(event)
        except engine.StopGameException as e:
            self.stop()
        finally:
            self.update_ui()

    def paintEvent(self, event):
        for i in range(self.BHeight):
            for j in range(self.BWidth):
                self.draw_square(j * self.scale_width(), i * self.scale_height(), abs(self.engine.cell(i, j)))

    def update_ui(self):
        if self.isStarted and not self.isPaused:
            self.msg2Statusbar.emit(f'Lines: {self.engine.total_lines()}')
        self.update()

    def draw_square(self, w, h, color_index):
        """ отрисовка квадратика """
        painter = QPainter(self)
        color = QColor(self.ColorTable[color_index])

        if color_index == 0:
            painter.fillRect(w, h, self.scale_width(), self.scale_height(), color)
            return

        painter.fillRect(w + 1, h + 1, self.scale_width() - 2, self.scale_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(w, h + self.scale_height() - 1, w, h)
        painter.drawLine(w, h, w + self.scale_width() - 1, h)

        painter.setPen(color.darker())
        painter.drawLine(w + 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + self.scale_height() - 1)
        painter.drawLine(w + self.scale_width() - 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + 1)
