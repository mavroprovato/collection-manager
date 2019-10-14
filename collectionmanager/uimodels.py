import os
import PyQt5.QtCore as QtCore


class TrackModel(QtCore.QAbstractTableModel):
    """The table model for track data.
    """
    columns = ['Directory', 'File Name', 'Album Artist', 'Album', 'Disk Number', 'Track Number', 'Artist', 'Track']

    def __init__(self, parent, db):
        """Create the track table model.

        :param parent: The parent window.
        :param db: The track database.
        """
        super(TrackModel, self).__init__(parent)

        self.db = db
        self.modelData = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.modelData)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(TrackModel.columns)

    def headerData(self, section, orientation, *args, **kwargs):
        if args[0] == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return TrackModel.columns[section]

    def data(self, index, role=None):
        if role == QtCore.Qt.DisplayRole:
            return self.modelData[index.row()][index.column()]

    def refresh(self):
        """Refresh the model.
        """
        self.modelData = self.db.track_data()
        self.modelReset.emit()

    def file_path_for(self, index):
        """Return the file path for the track at the specified index.

        :param index: The model index.
        :return: The file path for the track.
        """
        row_data = self.modelData[index.row()]

        return os.path.join(row_data[0], row_data[1])
