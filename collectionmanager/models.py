import PyQt5.QtCore as QtCore


class TrackModel(QtCore.QAbstractTableModel):
    columns = ['Artist', 'Album', 'Track']

    def __init__(self, parent, db):
        super(TrackModel, self).__init__(parent)

        self.model_data = db.track_data()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.model_data)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(TrackModel.columns)

    def headerData(self, section, orientation, *args, **kwargs):
        if args[0] == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return TrackModel.columns[section]

    def data(self, index, role=None):
        if role == QtCore.Qt.DisplayRole:
            return self.model_data[index.row()][index.column()]
