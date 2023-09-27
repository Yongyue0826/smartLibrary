# import sys
# import csv
# from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget
# from PyQt5.QtGui import QColor
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import csv
import sys
import os


class CSVTable(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the main window
        self.setWindowTitle("CSV Data Table")
        self.setGeometry(100, 100, 800, 400)

        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()

        # Create the table widget
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Load data from CSV and populate the table
        self.load_data_from_csv("test.csv")

        # Set the layout for the central widget
        central_widget.setLayout(layout)

    def load_data_from_csv(self, filename):
        # Read data from the CSV file
        with open(filename, "r") as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)

        # Set the number of rows and columns in the table
        num_rows = len(data)
        num_columns = len(data[0]) + 1  # Add an extra column for the "View" button

        self.table_widget.setRowCount(num_rows)
        self.table_widget.setColumnCount(num_columns)

        # Populate the table with data
        for row_index, row_data in enumerate(data):
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.table_widget.setItem(row_index, col_index, item)

            # Add a "View" button in the last column with a blue rectangle
            view_button = QPushButton("View")
            view_button.setStyleSheet("background-color: blue; color: white;")
            self.table_widget.setCellWidget(row_index, num_columns - 1, view_button)

            # Connect the button click event to a function
            view_button.clicked.connect(self.view_button_clicked)

    def view_button_clicked(self):
        # Handle the button click event here
        print("View button clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVTable()
    window.show()
    sys.exit(app.exec_())

#https://www.youtube.com/watch?v=a6_5vkxLwAw