import sys
import PyQt5.QtWidgets as Widgets


class MainWindow(Widgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Collection Manager')
        self.show()


def main():
    app = Widgets.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()