import PyQt5.QtCore as QtCore


class TrackModel(QtCore.QAbstractTableModel):
    columns = ['Artist', 'Album', 'Track']

    def __init__(self, parent, db):
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
        self.modelData = self.db.track_data()
        self.modelReset.emit()