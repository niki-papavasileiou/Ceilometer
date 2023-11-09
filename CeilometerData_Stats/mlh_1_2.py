import os
import pandas as pd
from CeilometerData import *

# if __name__ == '__main__':
#     folder_path = r"E:\may"
#     folder_path_out = r"C:\Users\nikip\Desktop\ceilometer_hours"
#     processor = CeilometerData(folder_path, folder_path_out)
#     processor.process_csv_files()

folder_path_out = r"C:\Users\nikip\Desktop\ceilometer_hours"
# Columns to compute the average for
mixing_layer_columns = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']

# Initialize a list to store the average values
averages = []
weighted_averages = []
medians = []
max=[]
min=[]
std_w = []
std_c=[]
file_len =[]

# Loop through each hour file
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

# Convert the list of averages into a DataFrame
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

# Save the DataFrame into a new CSV file
output_file = os.path.join(folder_path_out, "hourly_averages.csv")
final_df.to_csv(output_file, index=False)

#_____________________________________________________________________
import pandas as pd
import matplotlib.pyplot as plt
import calendar

file_path = os.path.join(folder_path_out, f"data_for_hour_0.csv")
month = pd.read_csv(file_path)
month['UTC Timestamp'] = pd.to_datetime(month['UTC Timestamp'])
unique_months = month['UTC Timestamp'].dt.month.unique()
month_names = [calendar.month_name[month] for month in unique_months]

data = pd.read_csv(output_file)

plt.figure(figsize=(12, 6))

# Plot each column
for column in data.columns[1:]:
    plt.plot(data['Hour'], data[column], label=column)

title = "Hourly Data Visualization ({})".format(', '.join(month_names))
plt.title(title)
plt.xlabel("Hour")
plt.ylabel("Value")
plt.legend()

plt.grid(True)
plt.tight_layout()
plt.show()
#______________________________________________________________________

#______________________________________________________________________
confirmation = input("Do you want to delete the contents of the files? (yes/no): ")

if confirmation.lower() == 'yes':
    for filename in os.listdir(folder_path_out):
        file_path = os.path.join(folder_path_out, filename)
        with open(r"C:\Users\nikip\Desktop\conf\statistics.csv", 'w') as file:
                pass
        with open(file_path, 'w') as file:
            pass
        for filename in os.listdir(r"E:\may"):
            if "merged" in filename:
                file_path = os.path.join(r"E:\may", filename)
                os.remove(file_path)
    print("Contents deleted successfully!")
else:
    print("Contents not deleted.")