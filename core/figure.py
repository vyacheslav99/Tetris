import copy


class Figure(object):

    FIG_TYPE_NONE = 0
    FIG_TYPE_SQUIRE = 1
    FIG_TYPE_LINE = 2
    FIG_TYPE_Z = 3
    FIG_TYPE_S = 4
    FIG_TYPE_T = 5
    FIG_TYPE_RL = 6
    FIG_TYPE_LL = 7

    FigOffsets = ( # (top, left) точки, отсчет стандартный - от лево-верха - вправо-низ
        ((0, 0), (0, 0), (0, 0), (0, 0)),   # нет фигуры
        ((0, 0), (0, 1), (1, 0), (1, 1)),   # Квадрат
        ((-1, 0), (0, 0), (1, 0), (2, 0)),  # Линия
        ((0, -1), (0, 0), (1, 0), (1, 1)),  # Z
        ((0, 0), (0, 1), (1, -1), (1, 0)),  # S
        ((0, -1), (0, 0), (0, 1), (1, 0)),  # T
        ((-1, 0), (0, 0), (1, 0), (1, 1)),  # L
        ((-1, 0), (0, 0), (1, 0), (1, -1))  # L, повернутая влево
    )

    def __init__(self, fig_type):
        self.fig_type = fig_type
        self.offsets = [[el[0], el[1]] for el in Figure.FigOffsets[fig_type]]
        self.prew_offsets = None

    def rotate_left(self):
        # повернуть против часовой стрелки
        if self.fig_type in (Figure.FIG_TYPE_NONE, Figure.FIG_TYPE_SQUIRE):
            return

        self.prew_offsets = copy.deepcopy(self.offsets)

        for item in self.offsets:
            item[0], item[1] = item[1], -item[0]

    def rotate_right(self):
        # повернуть по часовой стрелке
        if self.fig_type in (Figure.FIG_TYPE_NONE, Figure.FIG_TYPE_SQUIRE):
            return

        self.prew_offsets = copy.deepcopy(self.offsets)

        for item in self.offsets:
            item[0], item[1] = -item[1], item[0]

    def rollback(self):
        if self.prew_offsets:
            self.offsets = self.prew_offsets

    def get_center_index(self):
        for i in range(len(self.offsets)):
            if self.offsets[i] == [0, 0]:
                return i
