"""The main application widget
"""
import PyQt5.QtWidgets as QtWidgets

import collectionmanager.uimodels as models
import collectionmanager.ui.main_widget as main_widget
from collectionmanager.dialogs import TrackDetailDialog


class MainWidget(QtWidgets.QWidget, main_widget.Ui_Form):
    """The main application widget
    """
    def __init__(self, parent, db):
        """Constructor for the main application widget.

        :param parent: The parent widget.
        :param db: The database.
        """
        super(MainWidget, self).__init__(parent)

        self.libraryTableModel = models.TrackModel(self, db)
        self.trackDetailsDialog = TrackDetailDialog(self)

        self.setupUi()

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs: Keyword arguments.
        """
        super(MainWidget, self).setupUi(self)

        self.libraryTableView.setModel(self.libraryTableModel)
        self.libraryTableView.doubleClicked.connect(self.track_table_double_clicked)
        self.libraryTableModel.refresh()

    def track_table_double_clicked(self, index):
        """Called when the track table is double clicked.

        :param index: The model index.
        """
        file_path = self.libraryTableModel.file_path_for(index)
        self.trackDetailsDialog.set_file(file_path)
        self.trackDetailsDialog.exec_()
