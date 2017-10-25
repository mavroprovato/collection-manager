import PyQt5.QtWidgets as Widgets
import sys

import collectionmanager.ui.main_window as main_window


class CollectionManagerApp(Widgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CollectionManagerApp, self).__init__(parent)

        self.setupUi(self)


def main():
    app = Widgets.QApplication(sys.argv)
    form = CollectionManagerApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()