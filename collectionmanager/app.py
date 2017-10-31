"""
The application module
"""
import PyQt5.Qt as Qt
import PyQt5.QtSql as QtSql
import PyQt5.QtWidgets as QtWidgets
import sys

import collectionmanager.database as database
import collectionmanager.ui.main_window as main_window

app = None


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
        self.setup_ui()

    def setup_ui(self):
        super(CollectionManagerApp, self).setupUi(self)

        self.setCentralWidget(self.tableView)
        self.setup_actions()
        self.setup_data()

    def setup_actions(self):
        """
        Set up the application actions.
        """
        self.action_file_open.triggered.connect(self.open_directory)
        self.action_file_quit.triggered.connect(QtWidgets.qApp.quit)

    def setup_data(self):
        db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(database.DB_FILENAME)
        db.open()

        track_model = QtSql.QSqlQueryModel()
        track_model.setQuery("""
            SELECT al.name AS album, ar.name AS artist, f.track_number, f.track_name, f.relative_path, f.file_name
            FROM file f
            JOIN album al ON al.id = f.album_id
            JOIN artist ar ON ar.id = al.artist_id
        """, db)
        self.tableView.setModel(track_model)

    def open_directory(self):
        """Called when the user selects a directory to open.
        """
        directory = Qt.QFileDialog.getExistingDirectory(parent=self)
        if directory:
            self.db.add_directory(directory)
            self.db.save()
            self.setup_data()


def main():
    """
    The main entry point of the application.
    """
    global app
    app = QtWidgets.QApplication(sys.argv)
    form = CollectionManagerApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
