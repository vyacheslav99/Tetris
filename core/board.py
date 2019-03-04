import random
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

from . figure import Figure


class Board(QFrame):

    msg2Statusbar = pyqtSignal(str)
    ColorTable = (0x000000, 0xCC6666, 0x66CC66, 0x6666CC, 0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00)
    BWidth = 10
    BHeight = 22
    Speed = 1000

    def __init__(self, parent):
        super().__init__(parent)

        self.isStarted = False
        self.isPaused = False
        self.locked = False

        self.linesRemoved = 0

        # матрица доски, содержит числа, означающие тип фигуры в данной точке
        self.board = [[0 for col in range(Board.BWidth)] for row in range(Board.BHeight)]

        # текущие координаты центра (точки со смещением 0,0) обыгрываемой в данный момент фигуры
        self.figRow = 0
        self.figCol = 0

        # объект текущей фигуры
        self.figure = None

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def clear(self):
        for row in range(Board.BHeight):
            for col in range(Board.BWidth):
                self.board[row][col] = Figure.FIG_TYPE_NONE

    def start(self):
        if self.isStarted:
            self.stop()

        self.linesRemoved = 0
        self.msg2Statusbar.emit(f'Lines: {self.linesRemoved}')
        self.clear()
        self.timer.start(Board.Speed, self)

    def stop(self):
        if not self.isStarted:
            return

        self.timer.stop()
        self.isStarted = False
        self.isPaused = False
        self.locked = False
        self.msg2Statusbar.emit(f'End. Lines: {self.linesRemoved}')
        self.update()

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit('-= paused =-')
            self.update()
        else:
            self.timer.start(Board.Speed, self)

    def scaleWidth(self):
        return self.contentsRect().width() // Board.BWidth

    def scaleHeight(self):
        return self.contentsRect().height() // Board.BHeight

    def calcPos(self, centerTop, centerLeft):
        return [[centerTop + offset[0], centerLeft + offset[1]] for offset in self.figure.offsets]

    def calcExtremums(self, positions):
        minRow = Board.BHeight
        maxRow = 0
        minCol = Board.BWidth
        maxCol = 0

        for i in positions:
            minRow = min(minRow, i[0])
            maxRow = max(maxRow, i[0])
            minCol = min(minCol, i[1])
            maxCol = max(maxCol, i[1])

        return minRow, minCol, maxRow, maxCol

    def newFigure(self):
        """
        Появление новой фигуры.
        создает новую случайную фигуру
        забивает новую фигуру на доске по координатам, согласно ее смещениям
          в процессе проверяет, если новая фигура где-то пересеклась с уже занятыми точками - вызывает процедуру
          гамовера
        """
        pass

    def fixDown(self):
        """
        фиксируем фигуру на полу
        вычисляем положение, как она становиться и записываем в доске новое состояние точек
        затем вызываем процедуру проверки и стирания полных линий
        """
        pass

    def clearFullLines(self):
        """
        прверка наличия заполненных линий на доске и стирание всех найденных
        """
        self.msg2Statusbar.emit(f'Lines: {self.linesRemoved}')

    def tryMove(self, newRow, newCol):
        """
        вычисляет и записывает новое положение точек на доске, согласно новым координатам фигуры и их смещению
        если новое положение недостижимо:
          если двигали влево/право - просто на выход
          если крутили (новые координаты будут равны текущим) - если возле стенок - сместить влево/право соотв. на
            достаточное кол-во клеток, иначе просто на выход
          если двигали вниз - вызвать процедуру фиксации фигуры внизу, затем появления новой фигуры

        перемещаем фигуру в новую позицию:
          - записываем новые координаты
          - рассчитываем и записываем на доске в новых точках тип фигуры
        """

        try:
            while self.locked:
                pass

            self.locked = True
            res = False

            pos = self.calcPos(newRow, newCol)
            minRow, minCol, maxRow, maxCol = self.calcExtremums(pos)

            self.update()
            return res
        finally:
            self.locked = False

    def dropDown(self):
        while self.tryMove(self.figRow + 1, self.figCol):
            pass

    def paintEvent(self, event):
        for i in range(Board.BHeight):
            for j in range(Board.BWidth):
                if self.board[i][j] != Figure.FIG_TYPE_NONE:
                    self.drawSquare(j * self.scaleWidth(), i * self.scaleHeight(), self.board[i][j])

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_S:
            self.start()

        elif key == Qt.Key_P:
            self.pause()

        elif self.isPaused:
            return

        elif key == Qt.Key_Left:
            self.tryMove(self.figRow, self.figCol - 1)

        elif key == Qt.Key_Right:
            self.tryMove(self.figRow, self.figCol + 1)

        elif key == Qt.Key_Down:
            self.figure.rotateRaight()
            self.tryMove(self.figRow, self.figCol)

        elif key == Qt.Key_Up:
            self.figure.rotateLeft()
            self.tryMove(self.figRow, self.figCol)

        elif key == Qt.Key_Space:
            self.dropDown()

        elif key == Qt.Key_D:
            self.tryMove(self.figRow + 1, self.figCol)

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.tryMove(self.figRow + 1, self.figCol)
        else:
            super(Board, self).timerEvent(event)

    def drawSquare(self, w, h, fig_type):
        painter = QPainter(self)
        color = QColor(self.ColorTable[fig_type])
        painter.fillRect(w + 1, h + 1, self.scaleWidth() - 2, self.scaleHeight() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(w, h + self.scaleHeight() - 1, w, h)
        painter.drawLine(w, h, w + self.scaleWidth() - 1, h)

        painter.setPen(color.darker())
        painter.drawLine(w + 1, h + self.scaleHeight() - 1, w + self.scaleWidth() - 1, h + self.scaleHeight() - 1)
        painter.drawLine(w + self.scaleWidth() - 1, h + self.scaleHeight() - 1, w + self.scaleWidth() - 1, h + 1)
