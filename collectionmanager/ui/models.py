import PyQt5.Qt as Qt
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from ..db.database import Database


class TrackModel(QtCore.QAbstractTableModel):
    """The table model for track data.
    """
    column_info = [
        {'name': 'Directory', 'source': 'directory.path'},
        {'name': 'File Name', 'source': 'file_name'},
        {'name': 'Album Artist', 'source': 'artist.name'},
        {'name': 'Artist', 'source': 'artist_name'},
        {'name': 'Album', 'source': 'album.name'},
        {'name': 'Disk Number', 'source': 'disk_number'},
        {'name': 'Track Number', 'source': 'number'},
        {'name': 'Track', 'source': 'name'},
    ]

    def __init__(self, parent: QtWidgets.QWidget, db: Database):
        """Create the track table model.

        :param parent: The parent window.
        :param db: The database.
        """
        super().__init__(parent)

        self.db = db
        self.rows = []

        self.refresh()

    def headerData(self, section, orientation, role=None) -> Qt.QVariant:
        """Returns the data for the given role and section in the header with the specified orientation.

        For horizontal headers, the section number corresponds to the column number. Similarly, for vertical headers,
        the section number corresponds to the row number.

        :param section: The section.
        :param orientation: The orientation.
        :param role: The role.
        :return: The header data.
        """
        if orientation == Qt.Qt.Horizontal and role == Qt.Qt.DisplayRole:
            return Qt.QVariant(self.column_info[section]['name'])

        return Qt.QVariant()

    def rowCount(self, parent=None, *args, **kwargs) -> int:
        """Returns the number of rows under the given parent. When the parent is valid it means that rowCount is
        returning the number of children of parent.

        :param parent: The parent.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The number of rows under the given parent.
        """
        return len(self.rows)

    def columnCount(self, parent=None, *args, **kwargs) -> int:
        """Returns the number of columns for the children of the given parent.

        :param parent: The parent.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: The number of columns.
        """
        return len(self.column_info)

    def data(self, index: QtCore.QModelIndex, role=None):
        """Returns the data stored under the given role for the item referred to by the index.

        :param index: The index.
        :param role: The role.
        :return: The data.
        """
        if not index.isValid() or role != Qt.Qt.DisplayRole:
            return Qt.QVariant()

        # Get the data
        row = self.rows[index.row()]
        field_name = self.column_info[index.column()]['source']
        data = row
        for field_name_part in field_name.split('.'):
            data = getattr(data, field_name_part)

        return data

    def refresh(self):
        """Refresh the model data from the database.
        """
        self.rows = self.db.tracks()
        self.layoutChanged.emit()
