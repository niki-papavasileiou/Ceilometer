import sys
import os
import pandas as pd
import calendar
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog, QRadioButton, QFrame
from PyQt5.QtCore import Qt
from CeilometerData import *
from stdout import *


class DataProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.redirect_stdout()

    def initUI(self):
        # Input Folder
        self.inputFolderLabel = QLabel("Input Folder:")
        self.inputFolderLineEdit = QLineEdit()
        self.browseInputButton = QPushButton("Browse")
        self.browseInputButton.clicked.connect(self.browseInputFolder)

        self.outputText = QTextEdit()
        self.outputText.setReadOnly(True)

        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.inputFolderLabel)
        inputLayout.addWidget(self.inputFolderLineEdit)
        inputLayout.addWidget(self.browseInputButton)

        inputFrame = QFrame()
        inputFrame.setLayout(inputLayout)

        # Output Folder
        self.outputFolderLabel = QLabel("Output Folder:")
        self.outputFolderLineEdit = QLineEdit()
        self.browseOutputButton = QPushButton("Browse")
        self.browseOutputButton.clicked.connect(self.browseOutputFolder)

        outputLayout = QHBoxLayout()
        outputLayout.addWidget(self.outputFolderLabel)
        outputLayout.addWidget(self.outputFolderLineEdit)
        outputLayout.addWidget(self.browseOutputButton)

        outputFrame = QFrame()
        outputFrame.setLayout(outputLayout)

        # Process Button
        self.processButton = QPushButton("Process Data")
        self.processButton.setFixedSize(100, 30)
        self.processButton.clicked.connect(self.process_data)

        centerLayout = QHBoxLayout()
        centerLayout.addStretch(1)
        centerLayout.addWidget(self.processButton)
        centerLayout.addStretch(1)

        # Output Text
        self.outputText = QTextEdit()
        self.outputText.setReadOnly(True)

        # Confirm Delete
        self.confirmLabel = QLabel("Delete File Contents?")
        self.yesRadioButton = QRadioButton("Yes")
        self.noRadioButton = QRadioButton("No")
        self.noRadioButton.setChecked(True)
        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.clicked.connect(self.confirm_delete)

        # Clear Button
        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.clear_output)

        deleteLayout = QHBoxLayout()
        deleteLayout.addWidget(self.yesRadioButton)
        deleteLayout.addWidget(self.noRadioButton)
        deleteLayout.addStretch(1)

        # Layout for Confirm and Clear Buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.confirmButton)
        buttonLayout.addStretch(1)  
        buttonLayout.addWidget(self.clearButton)

        confirmLayout = QVBoxLayout()
        confirmLayout.addWidget(self.confirmLabel)
        confirmLayout.addLayout(deleteLayout)
        confirmLayout.addLayout(buttonLayout)  

        confirmFrame = QFrame()
        confirmFrame.setLayout(confirmLayout)

        # Main Layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(inputFrame)
        mainLayout.addWidget(outputFrame)
        mainLayout.addLayout(centerLayout)
        mainLayout.addWidget(self.outputText)
        mainLayout.addWidget(confirmFrame) 
        
        self.setLayout(mainLayout)
        self.setWindowTitle('Data Processor')

    def redirect_stdout(self):
        sys.stdout = TextRedirector(self.outputText)

    def clear_output(self):
        # Clear the text in the output text box
        self.outputText.clear()

    def browseInputFolder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.inputFolderLineEdit.setText(directory)

    def browseOutputFolder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.outputFolderLineEdit.setText(directory)

    def process_data(self):
        folder_path = self.inputFolderLineEdit.text()
        folder_path_out = self.outputFolderLineEdit.text()

        processor = CeilometerData(folder_path, folder_path_out)
        processor.process_csv_files()

        mixing_layer_columns = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']

        averages = []
        weighted_averages = []
        medians = []
        max=[]
        min=[]
        std_w = []
        std_c=[]
        file_len =[]

        for hour in range(24):
            file_path = os.path.join(folder_path_out, f"data_for_hour_{hour}.csv")
            
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                file_len.append((hour, len(df)))

                df['Row-wise Weighted Average'] = (df['Mixing Layer 2( Meters )'] * 2 + df['Mixing Layer 3( Meters )'] * 3) / 5
                df.to_csv(file_path, index=False)

                df['Row-wise Average'] = df[mixing_layer_columns].mean(axis=1)
                df.to_csv(file_path, index=False)

                median_val = df['Row-wise Weighted Average'].median()
                medians.append((hour, median_val))

                max_val = df['Row-wise Weighted Average'].max()
                max.append((hour, max_val))

                min_val = df['Row-wise Weighted Average'].min()
                min.append((hour, min_val))

                std_val_w = df['Row-wise Weighted Average'].std()
                std_w.append((hour, std_val_w))

                std_val_c = df['Row-wise Average'].std()
                std_c.append((hour, std_val_c))

                total_rows = len(df)
                sum_values = df[mixing_layer_columns].sum().sum()
                avg = sum_values / (2*total_rows) if total_rows > 0 else 0

                weighted_sum = (df['Mixing Layer 2( Meters )'] * 2).sum() + (df['Mixing Layer 3( Meters )'] * 3).sum()
                weighted_avg = weighted_sum / (5 * total_rows) if total_rows > 0 else 0
                
                averages.append((hour, avg))
                weighted_averages.append((hour, weighted_avg))

        avg_df = pd.DataFrame(averages, columns=['Hour', 'Average'])
        weighted_avg_df = pd.DataFrame(weighted_averages, columns=['Hour', 'Weighted Average'])
        median_df = pd.DataFrame(medians, columns=['Hour', 'Median'])
        max_df = pd.DataFrame(max, columns=['Hour', 'Max'])
        min_df = pd.DataFrame(min, columns=['Hour', 'Min'])
        std_w_df = pd.DataFrame(std_w, columns=['Hour', 'Standard Deviation(W.Avg)'])
        std_c_df = pd.DataFrame(std_c, columns=['Hour', 'Standard Deviation(Avg)'])
        lengths_df = pd.DataFrame(file_len, columns=['Hour', 'n of Observations'])

        final_df = pd.merge(avg_df, weighted_avg_df, on='Hour')
        final_df = pd.merge(final_df, median_df, on='Hour')
        final_df = pd.merge(final_df, max_df, on='Hour')
        final_df = pd.merge(final_df, min_df, on='Hour')
        final_df = pd.merge(final_df, std_w_df, on='Hour')
        final_df = pd.merge(final_df, std_c_df, on='Hour')
        final_df = pd.merge(final_df, lengths_df, on='Hour')

        output_file = os.path.join(folder_path_out, "hourly_averages.csv")
        final_df.to_csv(output_file, index=False)

        file_path = os.path.join(folder_path_out, f"data_for_hour_0.csv")
        month = pd.read_csv(file_path)
        month['UTC Timestamp'] = pd.to_datetime(month['UTC Timestamp'])
        unique_months = month['UTC Timestamp'].dt.month.unique()
        month_names = [calendar.month_name[month] for month in unique_months]

        data = pd.read_csv(output_file)

        plt.figure(figsize=(12, 6))

        for column in data.columns[1:]:
            plt.plot(data['Hour'], data[column], label=column)

        title = "Hourly Data Visualization for {}".format(', '.join(month_names))
        plt.title(title)
        plt.xlabel("Hour")
        plt.ylabel("Height")
        plt.legend()

        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
    def confirm_delete(self):
        folder_path = self.inputFolderLineEdit.text()
        folder_path_out = self.outputFolderLineEdit.text()
        confirmation = self.yesRadioButton.isChecked()
        if confirmation == 'yes':
            for filename in os.listdir(folder_path_out):
                file_path = os.path.join(folder_path_out, filename)
                with open("statistics.csv", 'w') as file:
                        pass
                with open(file_path, 'w') as file:
                    pass
                for filename in os.listdir(folder_path):
                    if "merged" in filename:
                        file_path = os.path.join(folder_path, filename)
                        os.remove(file_path)
        self.outputText.append("Contents deleted successfully!\n" if self.yesRadioButton.isChecked() else "Contents not deleted.\n")

def main():
    app = QApplication(sys.argv)
    ex = DataProcessor()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
