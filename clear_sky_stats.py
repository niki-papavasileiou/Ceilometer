#threshold 95, mean, mixing layer 2-3, dif 800m

import matplotlib.pyplot as plt
import pandas as pd
import os
import ast
import re 

folder_path = r"PATH"
folder_path_out = r"PATH"

def calculate_classical_avg(df):
    numeric_cols = ['Mixing Layer 1( Meters )','Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']
    
    initial_rows = len(df)  # Number of initial rows
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # col_diff = df[numeric_cols[1]] - df[numeric_cols[0]]
    # filtered_df = df[abs(col_diff) <= 800]

    # Calculate the absolute differences between the three columns
    col_diff_1_2 = df[numeric_cols[1]] - df[numeric_cols[0]]
    col_diff_2_3 = df[numeric_cols[2]] - df[numeric_cols[1]]
    col_diff_1_3 = df[numeric_cols[2]] - df[numeric_cols[0]]
    
    # Filter out rows where any of the absolute differences is greater than 800
    filtered_df = df[
        (abs(col_diff_1_2) <= 800) &
        (abs(col_diff_2_3) <= 800) &
        (abs(col_diff_1_3) <= 800)
    ]
    
    final_rows = len(filtered_df)  # Number of terminal rows
    
    # Calculate the classical average for the filtered data
    avg = filtered_df[numeric_cols].mean(axis=1)
    
    print(f"Initial rows: {initial_rows}")
    print(f"final rows: {final_rows}")
    
    return avg

def stats():
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    if len(csv_files) == 0:
        print("No CSV files found in the directory.")
        return

    # Initialize an empty DataFrame to hold all the statistics
    all_stats_df = pd.DataFrame()

    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        df = pd.read_csv(file_path, delimiter=',')

        df['UTC Timestamp'] = pd.to_datetime(df['UTC Timestamp'])
        df['Hour'] = df['UTC Timestamp'].dt.hour
        df['Mixing Layer 3( Meters )'] = pd.to_numeric(df['Mixing Layer 3( Meters )'], errors='coerce')
        df['Mixing Layer 1( Meters )'] = pd.to_numeric(df['Mixing Layer 1( Meters )'], errors='coerce')
        df.loc[:, 'Thickness'] = df['Mixing Layer 3( Meters )'] - df['Mixing Layer 1( Meters )']

        df['date'] = pd.to_datetime(df['UTC Timestamp']).dt.strftime('%d%m%y')
        df['Weighted Avg'] = calculate_classical_avg(df)

        percentage1 = df['Sky Condition 1( Oktas )'].value_counts(normalize=True) * 100
        percentage2 = df['Sky Condition 2( Oktas )'].value_counts(normalize=True) * 100
        percentage3 = df['Sky Condition 3( Oktas )'].value_counts(normalize=True) * 100
        percentage4 = df['Sky Condition 4( Oktas )'].value_counts(normalize=True) * 100
        percentage5 = df['Sky Condition 5( Oktas )'].value_counts(normalize=True) * 100

        stats_dict = {
            'Type': 'General',
            'date': df['date'].iloc[0],
            'Weighted Avg': df['Weighted Avg'].max(),
            'Weighted Avg': df['Weighted Avg'].min(),
            'Sky Condition 1( Oktas ) Distribution': percentage1.to_dict(),
            'Sky Condition 2( Oktas ) Distribution': percentage2.to_dict(),
            'Sky Condition 3( Oktas ) Distribution': percentage3.to_dict(),
            'Sky Condition 4( Oktas ) Distribution': percentage4.to_dict(),
            'Sky Condition 5( Oktas ) Distribution': percentage5.to_dict(),
        }

        # Convert the dictionary into a DataFrame
        stats_df = pd.DataFrame([stats_dict])

        # Append the statistics for the current file to the overall DataFrame
        all_stats_df = pd.concat([all_stats_df, stats_df], ignore_index=True)

        # Add the 'Weighted Avg' column to the original DataFrame and save it back to the CSV file
        df.to_csv(file_path, index=False)

    # Save all the statistics to a CSV file
    filename = 'statistics.csv'

    if not os.path.isfile(filename):
        open(filename, 'w').close()

    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        all_stats_df.to_csv(filename, mode='a', index=False, header=False)
    else:
        all_stats_df.to_csv(filename, mode='w', index=False)

stats()

df_s = pd.read_csv('statistics.csv', delimiter=',', dtype={'date': str})
indices_value_over_90 = []

columns_to_consider = ['Sky Condition 1( Oktas ) Distribution', 'Sky Condition 2( Oktas ) Distribution',
                       'Sky Condition 3( Oktas ) Distribution', 'Sky Condition 4( Oktas ) Distribution',
                       'Sky Condition 5( Oktas ) Distribution']

total_occurrences = 0
number_occurrences = {i: 0 for i in range(9)}

# Iterate through columns and count occurrences
for column in columns_to_consider:
    for row in df_s[column]:
        dictionary_data = ast.literal_eval(row)  # Convert string to dictionary
        total_occurrences += sum(dictionary_data.values())  # Add occurrences to the total
        for num in range(9):
            number_occurrences[num] += dictionary_data.get(num, 0)  # Add occurrences of each number

# Calculate and print the overall frequency of each number as a percentage
print("Overall Frequencies:")
for num in range(9):
    percentage = (number_occurrences[num] / total_occurrences) * 100
    print(f"Number {num}: {percentage:.2f}%")

# Iterate over the rows of the 'Sky Condition 2( Oktas ) Distribution' column
for index, row in enumerate(df_s['Sky Condition 1( Oktas ) Distribution']):
    # Convert the string representation of the dictionary to an actual dictionary
    dictionary_data = ast.literal_eval(row)
    
    # Extract the value corresponding to key 0 from the dictionary in each row
    value_at_0 = dictionary_data.get(0, 0)  # If key 0 doesn't exist, return 0 as default value
    
    if value_at_0 > 95:
        indices_value_over_90.append(index)
        # Get the values in the 'date' column for the indices
        mask = df_s.index.isin(indices_value_over_90)

        # Filter the 'date' column based on the mask and print the values
        dates_value_over_90 = df_s.loc[mask, 'date']

date_pattern = re.compile(r"\d{2}\d{2}\d{2}")

def check_date_in_filenames(folder_path, date):
    matching_filenames = []
    for filename in os.listdir(folder_path):
        if date_pattern.search(filename):
            if date in date_pattern.search(filename).group():
                matching_filenames.append(filename)
    return matching_filenames

dates_value_over_90 = list(map(str, dates_value_over_90))

# Initialize an empty DataFrame to hold all hourly averages
all_hourly_avg_df = pd.DataFrame()

for date in dates_value_over_90:
    matching_filenames = check_date_in_filenames(folder_path, date)
    if matching_filenames:
        print(f"Date {date} exists in filenames in the following files:")
        for filename in matching_filenames:
            print(filename)
        
        # Perform further analysis for files with this date
        # Loop over the matching_filenames list and read each file into a DataFrame
        for filename in matching_filenames:
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, delimiter=',')
            
            # Extract 'UTC Timestamp' and 'Weighted Avg' columns
            df['UTC Timestamp'] = pd.to_datetime(df['UTC Timestamp'])
            df['Weighted Avg'] = pd.to_numeric(df['Weighted Avg'], errors='coerce')
            df = df[['UTC Timestamp', 'Weighted Avg']]
            
            # Set 'UTC Timestamp' as the DataFrame index
            df.set_index('UTC Timestamp', inplace=True)
            
            # Resample the data with 1-hour frequency and calculate the hourly average
            hourly_avg_df = df.resample('1H').mean()
            
            # Append the hourly_avg_df DataFrame to the all_hourly_avg_df DataFrame
            all_hourly_avg_df = pd.concat([all_hourly_avg_df, hourly_avg_df])
    else:
        print(f"Date {date} does not exist in filenames.")

output_filename = 'all_hourly_averages.csv'
output_file_path = os.path.join(folder_path_out, output_filename)
all_hourly_avg_df.to_csv(output_file_path)

print(f"All hourly average data saved to: {output_file_path}")


########################################################################################


# data = pd.read_csv(output_file_path, delimiter=',')
# data['UTC Timestamp'] = pd.to_datetime(data['UTC Timestamp'])

# # Extract the hour from the 'UTC Timestamp' column
# data['Hour'] = data['UTC Timestamp'].dt.hour
# data['Hour'] = data['Hour'].apply(lambda x: f'{x:02d}:00')

# # Group by hour, and calculate the average of the 'Weighted Avg' column
# grouped_data_avg = data.groupby('Hour')['Weighted Avg'].mean().reset_index()
# grouped_data_max = data.groupby('Hour')['Weighted Avg'].max().reset_index()
# grouped_data_min = data.groupby('Hour')['Weighted Avg'].min().reset_index()
# grouped_data_std = data.groupby('Hour')['Weighted Avg'].std().reset_index()

# plt.plot(grouped_data_avg['Hour'], grouped_data_avg['Weighted Avg'], label='Average')
# plt.plot(grouped_data_max['Hour'], grouped_data_max['Weighted Avg'], label='Maximum')
# plt.plot(grouped_data_min['Hour'], grouped_data_min['Weighted Avg'], label='Minimum')
# plt.plot(grouped_data_std['Hour'], grouped_data_std['Weighted Avg'], label='Standard Deviation')

# plt.xlabel('Hour')
# plt.ylabel('Height')
# plt.legend()

# plt.show()

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv(output_file_path, delimiter=',')
data['UTC Timestamp'] = pd.to_datetime(data['UTC Timestamp'])

# Extract month and hour from the 'UTC Timestamp' column
data['Month'] = data['UTC Timestamp'].dt.month
data['Hour'] = data['UTC Timestamp'].dt.hour
data['Hour'] = data['Hour'].apply(lambda x: f'{x:02d}:00')

# Group by month and hour, and calculate the required statistics
grouped_data = data.groupby(['Month', 'Hour'])['Weighted Avg'].agg(['mean', 'max', 'min', 'std']).reset_index()

# Create subplots for each month
unique_months = grouped_data['Month'].unique()

for month in unique_months:
    month_data = grouped_data[grouped_data['Month'] == month]

    plt.figure(figsize=(10, 6))
    plt.plot(month_data['Hour'], month_data['mean'], label='Average')
    plt.plot(month_data['Hour'], month_data['max'], label='Maximum')
    plt.plot(month_data['Hour'], month_data['min'], label='Minimum')
    plt.plot(month_data['Hour'], month_data['std'], label='Standard Deviation')

    plt.xlabel('Hour')
    plt.ylabel('Height')
    plt.title(f'Statistics for Month {month}')
    plt.legend()
    plt.grid()

    plt.show()
