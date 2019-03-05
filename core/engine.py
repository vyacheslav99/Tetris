import random

from . figure import Figure


class StopGameException(Exception):
    pass


class Engine(object):

    def __init__(self, board_width, board_height):
        self.__width = board_width
        self.__height = board_height
        self.__locked = False
        self.__linesRemoved = 0

        # матрица доски, содержит тип фигуры в заданной точке
        self.__board = []

        # текущие координаты центра (точки со смещением 0,0) обыгрываемой в данный момент фигуры
        self.__figCenterRow = 0
        self.__figCenterCol = 0

        # объект текущей фигуры
        self.__figure = None

    def start(self):
        if not self.__figure:
            self.__new_figure()

    def clear(self):
        self.__locked = False
        self.__linesRemoved = 0
        self.__figure = None
        self.__board = [[Figure.FIG_TYPE_NONE for col in range(self.__width)] for row in range(self.__height)]

    def cell(self, top, left):
        return self.__board[top][left]

    def total_lines(self):
        return self.__linesRemoved

    def move_right(self):
        """ попытка переместить вправо """
        self.__try_move(self.__figCenterRow, self.__figCenterCol + 1)

    def move_left(self):
        """ попытка переместить влево """
        self.__try_move(self.__figCenterRow, self.__figCenterCol - 1)

    def move_down(self):
        """ попытка переместить вниз """
        self.__try_move(self.__figCenterRow + 1, self.__figCenterCol)

    def rotate_right(self):
        """ попытка провернуть вправо """
        self.__figure.rotate_right()
        self.__try_move(self.__figCenterRow, self.__figCenterCol)

    def rotate_left(self):
        """ попытка провернуть влево """
        self.__figure.rotate_right()
        self.__try_move(self.__figCenterRow, self.__figCenterCol)

    def drop_down(self):
        """ сбросить фигуру сразу вниз """
        while self.__try_move(self.__figCenterRow + 1, self.__figCenterCol):
            pass

    def __calc_pos(self, centerTop, centerLeft, prew_pos=False):
        """ вычисляет реальные координаты всех точек фигуры на доске от заданной точки центра по смещениям фигуры """
        offsets = self.__figure.prew_offsets if prew_pos and self.__figure.prew_offsets else self.__figure.offsets
        return [[centerTop + offset[0], centerLeft + offset[1]] for offset in offsets]

    def __calc_extremums(self, positions):
        """ вычисляет крайние значения набора координат """
        minRow = self.__height
        maxRow = 0
        minCol = self.__width
        maxCol = 0

        for i in positions:
            minRow = min(minRow, i[0])
            maxRow = max(maxRow, i[0])
            minCol = min(minCol, i[1])
            maxCol = max(maxCol, i[1])

        return minRow, minCol, maxRow, maxCol

    def __check_pos(self, pos):
        """ Проверяет, свободны ли на доске точки с заданными координатами """
        for coord in pos:
            if coord[0] < 0 or coord[0] >= self.__height or coord[1] < 0 or coord[1] >= self.__width \
                or self.__board[coord[0]][coord[1]] < 0:
                return False

        return True

    def __new_figure(self):
        """
        Появление новой фигуры.
        создает новую случайную фигуру
        забивает новую фигуру на доске по координатам, согласно ее смещениям
        в процессе проверяет, если новая фигура где-то пересеклась с уже занятыми точками - вызывает процедуру гамовера
        """

        self.__figure = Figure(random.randint(1, 7))

        self.__figCenterRow = 0
        self.__figCenterCol = self.__width // 2
        res = True
        top = 0

        pos = self.__calc_pos(top, self.__figCenterCol)
        minRow, minCol, maxRow, maxCol = self.__calc_extremums(pos)

        while minRow < 0:
            top += 1
            pos = self.__calc_pos(top, self.__figCenterCol)
            minRow, minCol, maxRow, maxCol = self.__calc_extremums(pos)

        self.__figCenterRow = pos[self.__figure.get_center_index()][0]

        if not self.__check_pos(pos):
            res = False

        for coord in pos:
            self.__board[coord[0]][coord[1]] = self.__figure.fig_type

        if not res:
            raise StopGameException('Game over!')

    def __anchor(self, pos):
        for coord in pos:
            self.__board[coord[0]][coord[1]] = -self.__board[coord[0]][coord[1]]

    def __remove_line(self, rowNo):
        """ стирание переданной линии и сдвиг всего, что выше вниз на одну линию """
        self.__linesRemoved += 1

        for row in range(rowNo, 0, -1):
            canStop = True

            for col in range(len(self.__board[row])):
                self.__board[row][col] = self.__board[row - 1][col]
                canStop = canStop and self.__board[row][col] == Figure.FIG_TYPE_NONE

            if canStop:
                break

    def __clear_full_lines(self, start):
        """ прверка наличия заполненных линий на доске и стирание всех найденных """
        for row in range(start, -1, -1):
            canStop = True
            canRemove = True

            for col in range(len(self.__board[row])):
                canStop = canStop and self.__board[row][col] == Figure.FIG_TYPE_NONE

                if self.__board[row][col] == Figure.FIG_TYPE_NONE:
                    canRemove = False

            if canStop:
                # если все оказались пустыми - область завала закончилась, останавливаемся
                break

            if canRemove:
                self.__remove_line(row)
                self.__clear_full_lines(row)
                break

    def __try_move(self, newRow, newCol):
        """
        Центральный метод игры, обработка шага игры
        вычисляет и записывает новое положение точек на доске, согласно новым координатам фигуры и их смещению
        выполняет проверки, возможно ли поместить фигуру в новую позицию и соответствующие действия по итогу
        newRow, newCol - координаты нового центра фигуры
        """

        try:
            while self.__locked:
                pass

            self.__locked = True
            new_pos = self.__calc_pos(newRow, newCol)
            curr_pos = self.__calc_pos(self.__figCenterRow, self.__figCenterCol,
                                       prew_pos=(newCol == self.__figCenterCol and newRow == self.__figCenterRow))

            if not self.__check_pos(new_pos):
                # проверим, не вылезли ли новые координаты за левые/правые стенки или не воткнулись ли мы в
                # торчащую где-то на доске занятую клетку, если да, то:
                if newCol != self.__figCenterCol or (newCol == self.__figCenterCol and newRow == self.__figCenterRow):
                    # если это было движение влево/право или вращение - то ничего не меняем, выходим
                    if newCol == self.__figCenterCol and newRow == self.__figCenterRow:
                        # если это было вращение, надо вернуть в исходную
                        self.__figure.rollback()

                    return False
                else:
                    # это было движение вниз:
                    # фиксируем фигуру на полу
                    # проверяем и стираем полные линии
                    # затем создаем новую фигуру (т.е. переходим к новому циклу игры)
                    self.__anchor(curr_pos)
                    self.__clear_full_lines(self.__height - 1)
                    self.__new_figure()
                    return False

            # все ОК, можно двигать:
            # очищаем по текущим координатам точки на доске
            for coord in curr_pos:
                self.__board[coord[0]][coord[1]] = Figure.FIG_TYPE_NONE

            # фиксируем новые координаты цетра фигуры
            self.__figCenterRow = newRow
            self.__figCenterCol = newCol

            # заполняем по новым координатам точки на доске флагом типа фигуры
            for coord in new_pos:
                self.__board[coord[0]][coord[1]] = self.__figure.fig_type

            return True
        finally:
            self.__locked = False
