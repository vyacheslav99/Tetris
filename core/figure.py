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

    def rotateLeft(self):
        # повернуть против часовой стрелки
        for item in self.offsets:
            if self.fig_type in (Figure.FIG_TYPE_NONE, Figure.FIG_TYPE_SQUIRE):
                return
            else:
                item[0], item[1] = item[1], -item[0]
            # elif self.fig_type in (Figure.FIG_TYPE_Z, Figure.FIG_TYPE_S, Figure.FIG_TYPE_LINE):
            #     # меняем местами x и y
            #     item[0], item[1] = item[1], item[0]
            #
            #     if self.fig_type == Figure.FIG_TYPE_Z:
            #         # меняем знак у всех координат
            #         for i in (0, 3):
            #             self.offsets[i] = [[x * -1, y * -1] for x, y in self.offsets[i]]
            #
            #         # меняем местами первую и последнюю точки
            #         self.offsets[0], self.offsets[3] = self.offsets[3], self.offsets[0]
            #     elif self.fig_type == Figure.FIG_TYPE_S:
            #         # меняем местами рядом стоящие точки (0-1 и 2-3)
            #         for i in (1, 3):
            #             self.offsets[i-1], self.offsets[i] = self.offsets[i], self.offsets[i-1]
            #
            #         # меняем знак по одной из координат 2-х точек, в зависимости от положения это или x-ы или y-и
            #         for i in range(self.offsets):
            #             self.offsets[i][1 if i in (1, 2) else 0] *= -1


    def rotateRaight(self):
        # повернуть по часовой стрелке
        for item in self.offsets:
            if self.fig_type in (Figure.FIG_TYPE_NONE, Figure.FIG_TYPE_SQUIRE):
                return
            else:
                item[0], item[1] = -item[1], item[0]
