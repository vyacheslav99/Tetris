import random
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

from . figure import Figure


class Board(QFrame):

    msg2Statusbar = pyqtSignal(str)
    ColorTable = (0xECE9D8, 0xCC6666, 0x66CC66, 0x6666CC, 0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00)
    BWidth = 10
    BHeight = 22
    Speed = 1000

    def __init__(self, parent):
        super().__init__(parent)

        self.isStarted = False
        self.isPaused = False
        self.locked = False

        self.linesRemoved = 0

        # матрица доски, содержит тип фигуры в заданной точке
        self.board = []

        # текущие координаты центра (точки со смещением 0,0) обыгрываемой в данный момент фигуры
        self.figRow = 0
        self.figCol = 0

        # объект текущей фигуры
        self.figure = None

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def clear(self):
        self.figure = None
        self.board = [[Figure.FIG_TYPE_NONE for col in range(Board.BWidth)] for row in range(Board.BHeight)]

    def start(self):
        if self.isStarted:
            self.stop()

        self.isStarted = True
        self.linesRemoved = 0
        self.msg2Statusbar.emit(f'Lines: {self.linesRemoved}')
        self.clear()
        self.new_figure()
        self.update()
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

    def scale_width(self):
        """ масштабирование - рассчитывает размер стороны квадрата в пикселях по оси X (ширина) """
        return self.contentsRect().width() // Board.BWidth

    def scale_height(self):
        """ масштабирование - рассчитывает размер стороны квадрата в пикселях по оси Y (высота) """
        return self.contentsRect().height() // Board.BHeight

    def calc_pos(self, centerTop, centerLeft):
        """ вычисляет реальные координаты всех точек фигуры на доске от заданной точки центра по смещениям фигуры """
        return [[centerTop + offset[0], centerLeft + offset[1]] for offset in self.figure.offsets]

    def calc_extremums(self, positions):
        """ вычисляет крайние значения набора координат """
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

    def check_pos(self, pos):
        """ Проверяет, свободны ли на доске точки с заданными координатами """
        for coord in pos:
            if coord[0] < 0 or coord[0] >= Board.BHeight or coord[1] < 0 or coord[1] >= Board.BWidth or (
                coord not in pos and self.board[coord[0]][coord[1]] != Figure.FIG_TYPE_NONE):
                return False

        return True

    def new_figure(self):
        """
        Появление новой фигуры.
        создает новую случайную фигуру
        забивает новую фигуру на доске по координатам, согласно ее смещениям
        в процессе проверяет, если новая фигура где-то пересеклась с уже занятыми точками - вызывает процедуру гамовера
        """

        self.figRow = 0
        self.figCol = Board.BWidth // 2

        self.figure = Figure(random.randint(1, 7))
        top = 0
        pos = self.calc_pos(top, self.figCol)
        minRow, minCol, maxRow, maxCol = self.calc_extremums(pos)

        while minRow < 0:
            top += 1
            pos = self.calc_pos(top, self.figCol)
            minRow, minCol, maxRow, maxCol = self.calc_extremums(pos)

        self.figRow = pos[self.figure.get_center_index()][0]

        if not self.check_pos(pos):
            self.stop()

    def remove_line(self, rowNo):
        """ стирание переданной линии и сдвиг всего, что выше вниз на одну линию """
        self.linesRemoved += 1

        canStop = True

        for row in range(rowNo, -1, -1):
            for col in range(len(self.board[row])):
                self.board[row][col] = self.board[row][col] - 1
                canStop = canStop and self.board[row][col] == Figure.FIG_TYPE_NONE

            if canStop:
                break

    def clear_full_lines(self, start):
        """ прверка наличия заполненных линий на доске и стирание всех найденных """
        for row in range(start, -1, -1):
            canStop = True
            canRemove = True

            for col in range(len(self.board[row])):
                canStop = canStop and self.board[row][col] == Figure.FIG_TYPE_NONE

                if self.board[row][col] == Figure.FIG_TYPE_NONE:
                    canRemove = False

            if canStop:
                # если все оказались пустыми - область завала закончилась, останавливаемся
                break

            if canRemove:
                # сдвигаем
                self.remove_line(row)
                # продолжаем с текущей линии (т.к. на текущей позиции уже предыдущая)
                self.clear_full_lines(row)
                self.msg2Statusbar.emit(f'Lines: {self.linesRemoved}')
                self.update()
                break

    def try_move(self, newRow, newCol):
        """
        Центральный метод игры, обработка шага игры
        вычисляет и записывает новое положение точек на доске, согласно новым координатам фигуры и их смещению
        выполняет проверки, возможно ли поместить фигуру в новую позицию и соответствующие действия по итогу
        newRow, newCol - координаты нового центра фигуры
        """

        try:
            while self.locked:
                pass

            self.locked = True
            pos = self.calc_pos(newRow, newCol)

            if not self.check_pos(pos):
                # проверим, не вылезли ли новые координаты за левые/правые стенки или не воткнулись ли мы в
                # торчащую где-то на доске занятую клетку, если да, то:
                if newCol != self.figCol or (newCol == self.figCol and newRow == self.figRow):
                    # если это было движение влево/право или вращение - то ничего не меняем, выходим
                    if newCol == self.figCol and newRow == self.figRow:
                        # если это было вращение, надо вернуть в исходную
                        self.figure.rollback()

                    return False
                else:
                    # это было движение вниз:
                    # проверяем и стираем полные линии,
                    # затем создаем новую фигуру (т.е. переходим к новому циклу игры)

                    self.clear_full_lines(Board.BHeight - 1)
                    self.new_figure()
                    return False

            # все ОК, можно двигать:
            # очищаем по текущим координатам точки на доске
            for coord in self.calc_pos(self.figRow, self.figCol):
                self.board[coord[0]][coord[1]] = Figure.FIG_TYPE_NONE

            # фиксируем новые координаты цетра фигуры
            self.figRow = newRow
            self.figCol = newCol

            # заполняем по новым координатам точки на доске флагом типа фигуры
            for coord in pos:
                self.board[coord[0]][coord[1]] = self.figure.fig_type

            return True
        finally:
            self.update()
            self.locked = False

    def drop_down(self):
        """ сбросить фигуру сразу вниз """
        while self.try_move(self.figRow + 1, self.figCol):
            pass

    def paintEvent(self, event):
        for i in range(Board.BHeight):
            for j in range(Board.BWidth):
                self.draw_square(j * self.scale_width(), i * self.scale_height(), self.board[i][j])

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_S:
            self.start()

        elif key == Qt.Key_P:
            self.pause()

        elif not self.isStarted or self.isPaused:
            return

        elif key == Qt.Key_Left:
            self.try_move(self.figRow, self.figCol - 1)

        elif key == Qt.Key_Right:
            self.try_move(self.figRow, self.figCol + 1)

        elif key == Qt.Key_Down:
            self.figure.rotate_right()
            self.try_move(self.figRow, self.figCol)

        elif key == Qt.Key_Up:
            self.figure.rotate_left()
            self.try_move(self.figRow, self.figCol)

        elif key == Qt.Key_Space:
            self.drop_down()

        elif key == Qt.Key_D:
            self.try_move(self.figRow + 1, self.figCol)

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.try_move(self.figRow + 1, self.figCol)
        else:
            super(Board, self).timerEvent(event)

    def draw_square(self, w, h, fig_type):
        """ отрисовка квадратика """
        painter = QPainter(self)
        color = QColor(self.ColorTable[fig_type])

        if fig_type == Figure.FIG_TYPE_NONE:
            painter.fillRect(w, h, self.scale_width(), self.scale_height(), color)
            return

        painter.fillRect(w + 1, h + 1, self.scale_width() - 2, self.scale_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(w, h + self.scale_height() - 1, w, h)
        painter.drawLine(w, h, w + self.scale_width() - 1, h)

        painter.setPen(color.darker())
        painter.drawLine(w + 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + self.scale_height() - 1)
        painter.drawLine(w + self.scale_width() - 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + 1)
