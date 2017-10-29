"""
The application module
"""
import PyQt5.Qt as Qt
import PyQt5.QtSql as QtSql
import PyQt5.QtWidgets as QtWidgets
import sys

import collectionmanager.database as database
import collectionmanager.ui.main_window as main_window


class CollectionManagerApp(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    """
    The application class
    """
    def __init__(self, parent=None):
        """Constructor for the main application class.

        :param parent: The parent window.
        """
        super(CollectionManagerApp, self).__init__(parent)

        self.db = database.Database()

        self.setupUi(self)
        self.setup_actions()
        self.setup_data()

    def setup_actions(self):
        """
        Set up the application actions.
        """
        self.action_file_open.triggered.connect(self.open_directory)
        self.action_file_quit.triggered.connect(QtWidgets.qApp.quit)

    def setup_data(self):
        self.setCentralWidget(self.tableView)
        db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(database.DB_FILENAME)
        db.open()

        track_model = QtSql.QSqlQueryModel()
        track_model.setQuery("""
            SELECT a.name, f.relative_path, f.file_name
            FROM file f
            JOIN artist a ON a.id = f.artist_id
        """, db)
        self.tableView.setModel(track_model)

    def open_directory(self):
        """Called when the user selects a directory to open.
        """
        directory = Qt.QFileDialog.getExistingDirectory(parent=self)
        if directory:
            self.db.add_directory(directory)
            self.db.save()


def main():
    """
    The main entry point of the application.
    """
    app = QtWidgets.QApplication(sys.argv)
    form = CollectionManagerApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
