import sys
import pandas as pd
import numpy as np
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QFont, QTextOption

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Backscatter Profile")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.control_layout = QHBoxLayout()
        self.layout.addLayout(self.control_layout)

        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        self.control_layout.addWidget(self.upload_button)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot)
        self.control_layout.addWidget(self.plot_button)

        self.cmap_combobox = QComboBox()
        self.cmap_combobox.addItems(['gray', 'bone', 'bone_r','viridis', 'hsv', 'jet', 'gist_stern'])
        self.control_layout.addWidget(self.cmap_combobox)

        self.save_button = QPushButton("Save File")
        self.save_button.clicked.connect(self.save_file)
        self.control_layout.addWidget(self.save_button)

        self.text_area = QTextEdit()
        self.layout.addWidget(self.text_area)
        self.text_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        font = QFont("Courier")
        font.setPointSize(12)  
        self.text_area.setFont(font)
        self.text_area.setWordWrapMode(QTextOption.NoWrap)

    def upload_file(self):
        global hourly_averages
        file_path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.read_csv(file_path, delimiter=',')
                df['UTC Timestamp'] = pd.to_datetime(df['UTC Timestamp'])           
                df_split = df['Backscatter Profile( (100000*srad*km)^-1 )'].str.split(',', expand=True).apply(pd.to_numeric, errors='coerce')   
                df_split['UTC Timestamp'] = df['UTC Timestamp']                     
                grouped = df_split.groupby(df_split['UTC Timestamp'].dt.hour)       
                hourly_averages = grouped.mean(numeric_only=True)                    
                hourly_averages = hourly_averages.transpose()                       
                
                full_df_string = hourly_averages.to_string()  
                self.text_area.setText(full_df_string)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "CSV Files (*.csv)")
        if file_path:
            try:
                hourly_averages.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", "File saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def plot(self):
        cmap = self.cmap_combobox.currentText()
        hourly_averages.columns = pd.to_numeric(hourly_averages.columns, errors='coerce')
        hourly_averages.index = pd.to_numeric(hourly_averages.index, errors='coerce')

        cols, rows = np.meshgrid(hourly_averages.columns, hourly_averages.index)

        values = hourly_averages.values

        plt.figure(figsize=(12, 6))
        plt.contourf(cols, rows, values, levels=70, cmap=cmap)  
        plt.colorbar(label=' (100000*srad*km)^-1')
        plt.xlabel('Hour')
        plt.ylabel('Height')
        plt.title('Backscatter Profile')
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
