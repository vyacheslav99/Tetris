from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from . import board


class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tboard = board.Board(self)
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
