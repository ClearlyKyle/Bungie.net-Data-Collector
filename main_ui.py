from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot
import os, pandas, numpy


class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None


class MainWindow(QtWidgets.QMainWindow):
    send_fig = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_widget = QtWidgets.QWidget(self)

        self.fig, self.ax = pyplot.subplots()
        # self.fig, self.ax = pyplot.subplots(figsize=(13, 5))
        self.canvas = FigureCanvas(self.fig)

        # self.fig.subplots_adjust(0.070, 0.700, 0.880, 0.156)  # left,bottom,right,top
        # pyplot.legend(bbox_to_anchor=(1, 1.02))
        pyplot.xticks(rotation=45)
        pyplot.yticks(numpy.arange(0, 51, step=2))
        pyplot.ylim([0, 51])

        # self.ax.legend(bbox_to_anchor=(1, 1.02))
        pyplot.grid()
        pyplot.subplots_adjust(left=0.070, right=0.930, top=0.880, bottom=0.120)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        csv_files = []
        entries = os.listdir(".")
        for file in entries:
            if file.endswith("OUTPUT.csv"):
                csv_files.append(file)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        # self.createTable()

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        self.dropdown1 = QtWidgets.QComboBox()
        self.dropdown1.addItems(csv_files)
        # self.dropdown2.setCurrentIndex(0)

        self.dropdown1.currentIndexChanged.connect(self.update)
        # self.dropdown2.currentIndexChanged.connect(self.update)
        self.label = QtWidgets.QLabel("A plot:")

        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.layout.addWidget(QtWidgets.QLabel("Select File..."))
        self.layout.addWidget(self.dropdown1)
        self.layout.addWidget(self.tableWidget, 0, 1, 0, 3)

        self.layout.addWidget(self.canvas)

        self.setCentralWidget(self.main_widget)
        self.show()
        self.update()

    # Create table
    def updatetable(self, data):
        print("UPDATING TABLE")
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)

        print("> Table clear")
        # Row count

        player_names = '\n'.join(data['index'].to_list())
        player_name_count = '\n'.join(str(x) for x in data['players'])

        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(2)

        for i, row in enumerate(zip(data['index'].to_list(), data['players'])):
            print(row[1])
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(row[0]))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(row[1])))

        # Table will fit the screen horizontally
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)

    def update(self):
        # colors = ["b", "r", "g", "y", "k", "c"]
        # self.ax1.clear()
        self.ax.clear()
        selected_file = self.dropdown1.currentText()

        series = pandas.read_csv(selected_file,
                                 parse_dates=True,
                                 converters={'players': eval})

        if series.columns.tolist() != ['game mode', 'map', 'playlist', 'skill level', 'kills', 'assists', 'deaths',
                                       'spread', 'players', 'date', 'url']:
            print("Error with file")
            return

        series['date'] = pandas.to_datetime(series["date"])

        all_days = pandas.date_range(min(series['date']), max(series['date']), freq='D')

        temp_series = series.copy()
        temp_series.index = pandas.DatetimeIndex(series['date']).floor('D')
        new_df = series.join(all_days.to_frame(), how='outer').drop(0, 1)

        missing_dates_series = new_df.reset_index()

        most_played_with = series.explode('players')['players'].value_counts()[1:15].to_frame().reset_index()

        KD_spread_analysis = series['spread'].describe()

        games_per_day = missing_dates_series['date'].value_counts().sort_index()
        games_per_month = missing_dates_series.set_index('date').resample('MS').size()
        games_per_year = missing_dates_series.set_index('date').resample('YS').size()

        kd_spread_per_month = series.resample('MS', on='date')['spread'].sum()
        average_spread_per_month = series.resample('MS', on='date')['spread'].mean()

        playlists = series['playlist'].unique()
        self.ax.plot([], [], label="Playlist", linewidth=0)
        for game_mode in playlists:
            game = series[series['playlist'] == game_mode].sort_values(by="date", ascending=True)
            self.ax.plot(game['date'], game['skill level'], label=game_mode)

        self.ax.set_title(selected_file.strip('_OUTPUT.csv'))
        self.ax.grid()

        self.updatetable(most_played_with)

        self.fig.canvas.draw_idle()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
