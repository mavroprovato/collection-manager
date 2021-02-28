"""The main application widget
"""
import PyQt5.QtWidgets as QtWidgets

from collectionmanager.ui import models
import collectionmanager.ui.ui.main_widget as main_widget
from collectionmanager.ui.dialogs import TrackDetailDialog


class MainWidget(QtWidgets.QWidget, main_widget.Ui_Form):
    """The main application widget
    """
    def __init__(self, parent):
        """Constructor for the main application widget.

        :param parent: The parent widget.
        """
        super().__init__(parent)

        self.trackModel = models.TrackModel(self)
        self.trackDetailsDialog = TrackDetailDialog(self)

        self.setupUi()

    def setupUi(self, **kwargs):
        """Set up the user interface.

        :param kwargs: Keyword arguments.
        """
        super(MainWidget, self).setupUi(self)

        self.libraryTableView.setModel(self.trackModel)
        self.libraryTableView.doubleClicked.connect(self.track_table_double_clicked)
        self.trackModel.refresh()

    def track_table_double_clicked(self, index):
        """Called when the track table is double clicked.

        :param index: The model index.
        """
        track = self.trackModel.rows[index.row()]
        self.trackDetailsDialog.set_track(track)
        self.trackDetailsDialog.exec_()
