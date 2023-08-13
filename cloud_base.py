#weighted avg, dif 800m, mixing layer 2-3, 95

import matplotlib.pyplot as plt
import pandas as pd
import os
import ast
import re 

import warnings
pd.options.mode.chained_assignment = None  # default='war

folder_path = r"C:\Users\nikip\Desktop\testceilo"
folder_path_out = r"C:\Users\nikip\Desktop\results"

def calculate_weighted_avg(df):
    global df_filter, final_rows,initial_rows
    weights = [2, 3]
    numeric_cols = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']
    
    avg = sum(df[col] * weight for col, weight in zip(numeric_cols, weights))
    return avg / sum(weights)

def stats():
    global csv_files

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    if len(csv_files) == 0:
        print("No CSV files found in the directory.")
        return

    all_stats_df = pd.DataFrame()
    total_initial_rows = 0
    total_terminal_rows = 0
    total_cloudy_duration = 0

    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        df = pd.read_csv(file_path, delimiter=',')
        initial_rows = len(df)
        print(f"Initial rows: {initial_rows}")

        # numeric_cols = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']

        # for col in numeric_cols:
        #     df[col] = pd.to_numeric(df[col], errors='coerce')

        # col_diff = df[numeric_cols[1]] - df[numeric_cols[0]]
        # df_filter = df[abs(col_diff) < 1000]
        # final_rows = len(df_filter)

        # print(f"final rows: {final_rows}")

        def cloud_base(df):
            nan_string = "/////"
            percentage_nan_dict = {}
            total_cells_all_columns = 0
            total_nan_cells_all_columns = 0

            for col_num in range(1, 5):
                cloud_base_column = f"Cloud Base {col_num}( Meters )"
                nan_cells = df[cloud_base_column].eq(nan_string).sum()
                total_cells = df[cloud_base_column].size
                total_cells_all_columns += total_cells
                total_nan_cells_all_columns += nan_cells
                # percentage_nan = (nan_cells / total_cells) * 100
                percentage_nan = (nan_cells / total_cells) * 100 if total_cells > 0 else 0  
                percentage_nan_dict[cloud_base_column] = percentage_nan

            overall_percentage_nan = (total_nan_cells_all_columns / total_cells_all_columns) * 100 if total_cells_all_columns > 0 else 0
            percentage_nan_dict["Overall"] = overall_percentage_nan

            clear_sky_count = 0
            clear_sky_duration = pd.Timedelta(0)
            total_rows = len(df)

            for _, row in df.iterrows():
                is_clear_sky = all(row[f"Cloud Base {col_num}( Meters )"] == nan_string for col_num in range(1, 5))
                if is_clear_sky:
                    clear_sky_count += 1
                    clear_sky_duration += row["UTC Timestamp"] - df["UTC Timestamp"].iloc[0]  # Calculate clear sky duration


            clear_sky_percentage = (clear_sky_count / total_rows) * 100 if total_rows > 0 else 0
            percentage_nan_dict["Overall 2"] = clear_sky_percentage
        
            # cloudy_columns = ['Cloud Base 1( Meters )', 'Cloud Base 2( Meters )', 'Cloud Base 3( Meters )', 'Cloud Base 4( Meters )']
            # df['AllCloudy'] = df.apply(lambda row: all(row[col] == nan_string for col in cloudy_columns), axis=1)
            # df['TimeDiff'] = df['UTC Timestamp'].diff()
            # cloudy_duration_per_file = df.groupby('AllCloudy')['TimeDiff'].sum()
            # cloudy_duration = cloudy_duration_per_file.get(True, pd.Timedelta(0)).total_seconds()
    
            return percentage_nan_dict,clear_sky_duration#,clear_sky_duration#,clear_sky_duration,

        df['UTC Timestamp'] = pd.to_datetime(df['UTC Timestamp'])
        df['Hour'] = df['UTC Timestamp'].dt.hour
        df['Mixing Layer 3( Meters )'] = pd.to_numeric(df['Mixing Layer 3( Meters )'], errors='coerce')
        df['Mixing Layer 1( Meters )'] = pd.to_numeric(df['Mixing Layer 1( Meters )'], errors='coerce')
        df.loc[:, 'Thickness'] = df['Mixing Layer 3( Meters )'] - df['Mixing Layer 1( Meters )']

        df['date'] = pd.to_datetime(df['UTC Timestamp']).dt.strftime('%d%m%y')
        df['Weighted Avg'] = calculate_weighted_avg(df)
        
        numeric_cols = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        col_diff = df[numeric_cols[1]] - df[numeric_cols[0]]
        df_filter = df[abs(col_diff) < 800]
        final_rows = len(df_filter)

        print(f"final rows: {final_rows}")

        total_initial_rows += initial_rows
        total_terminal_rows += final_rows

        percentage1 = df['Sky Condition 1( Oktas )'].value_counts(normalize=True) * 100
        percentage2 = df['Sky Condition 2( Oktas )'].value_counts(normalize=True) * 100
        percentage3 = df['Sky Condition 3( Oktas )'].value_counts(normalize=True) * 100
        percentage4 = df['Sky Condition 4( Oktas )'].value_counts(normalize=True) * 100
        percentage5 = df['Sky Condition 5( Oktas )'].value_counts(normalize=True) * 100

        cloud_base_percentages,clear_sky_duration = cloud_base(df)
        # total_cloudy_duration += cloudy_duration

        # print("Cloudy Durations for Each Fe:")
        # print(f"File with Clouds: {clear_sky_duration} seconds")
        # print(f"  - Minutes: {clear_sky_duration / 60:.2f} minutes")
        # print(f"  - Hours: {clear_sky_duration/ 3600:.2f} hours")    

        stats_dict = {
            'Type': 'General',
            'date': df_filter['date'].iloc[0] if len(df_filter) > 0 else None,
            'Weighted Avg': df_filter['Weighted Avg'].max(),
            'Weighted Avg': df_filter['Weighted Avg'].min(),
            'Sky Condition 1( Oktas ) Distribution': percentage1.to_dict(),
            'Sky Condition 2( Oktas ) Distribution': percentage2.to_dict(),
            'Sky Condition 3( Oktas ) Distribution': percentage3.to_dict(),
            'Sky Condition 4( Oktas ) Distribution': percentage4.to_dict(),
            'Sky Condition 5( Oktas ) Distribution': percentage5.to_dict(),
            **cloud_base_percentages
        }

        # Convert the dictionary into a DataFrame
        stats_df = pd.DataFrame([stats_dict])

        # Append the statistics for the current file to the overall DataFrame
        all_stats_df = pd.concat([all_stats_df, stats_df], ignore_index=True)

        # Add the 'Weighted Avg' column to the original DataFrame and save it back to the CSV file
        df.to_csv(file_path, index=False)

    # print("Total Cloudy Duration:")
    # print(f"  - Seconds: {total_cloudy_duration:.2f} seconds")
    # print(f"  - Minutes: {total_cloudy_duration / 60:.2f} minutes")
    # print(f"  - Hours: {total_cloudy_duration / 3600:.2f} hours")
    
    # Save all the statistics to a CSV file
    filename = 'statistics.csv'

    if not os.path.isfile(filename):
        open(filename, 'w').close()

    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        all_stats_df.to_csv(filename, mode='a', index=False, header=False)
    else:
        all_stats_df.to_csv(filename, mode='w', index=False)

    print(f"Total initial rows across all files: {total_initial_rows}")
    print(f"Total final rows across all files: {total_terminal_rows}")

stats()

df_s = pd.read_csv('statistics.csv', delimiter=',', dtype={'date': str})
indices_value_over_90 = []

for index, value in enumerate(df_s['Overall 2']):
    if value > 95:
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
            numeric_cols = ['Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']

            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            col_diff = df[numeric_cols[1]] - df[numeric_cols[0]]
            df_filter = df[abs(col_diff) < 800]
            
            # df_filter['UTC Timestamp'] = pd.to_datetime(df_filter['UTC Timestamp'])
            df_filter.loc[:, 'UTC Timestamp'] = pd.to_datetime(df_filter['UTC Timestamp'])
            df_filter.loc[:, 'Weighted Avg'] = pd.to_numeric(df_filter['Weighted Avg'], errors='coerce')
            # df_filter['Weighted Avg'] = pd.to_numeric(df_filter['Weighted Avg'], errors='coerce')
            df_filter = df_filter[['UTC Timestamp', 'Weighted Avg']]
            
            # Set 'UTC Timestamp' as the DataFrame index
            df_filter.set_index('UTC Timestamp', inplace=True)
            
            # Resample the data with 1-hour frequency and calculate the hourly average
            hourly_avg_df = df_filter.resample('1H').mean()
            
            # Append the hourly_avg_df DataFrame to the all_hourly_avg_df DataFrame
            all_hourly_avg_df = pd.concat([all_hourly_avg_df, hourly_avg_df])
    else:
        print(f"Date {date} does not exist in filenames.")

output_filename = 'all_hourly_averages.csv'
output_file_path = os.path.join(folder_path_out, output_filename)
all_hourly_avg_df.to_csv(output_file_path)

n_valid_days = len(dates_value_over_90)
n_total_days = len(os.listdir(folder_path))

print(f"All hourly average data saved to: {output_file_path}")
print(f"Total days: {n_total_days}, Valid days: {n_valid_days}")
total_percentage = df_s['Overall 2'].sum() / len(df_s)
print(f"monthly percentage of clear sky: {total_percentage:.2f}%")

########################################################################################

data = pd.read_csv(output_file_path, delimiter=',')
data['UTC Timestamp'] = pd.to_datetime(data['UTC Timestamp'])

# Extract the hour from the 'UTC Timestamp' column
data['Hour'] = data['UTC Timestamp'].dt.hour
import calendar
data['Month'] = data['UTC Timestamp'].dt.month
data['Month'] = data['Month'].apply(lambda x: calendar.month_name[x])
data['Hour'] = data['Hour'].apply(lambda x: f'{x:02d}:00')

unique_months = data['Month'].unique()

# Group by hour, and calculate the average of the 'Weighted Avg' column
grouped_data_avg = data.groupby('Hour')['Weighted Avg'].mean().reset_index()
grouped_data_max = data.groupby('Hour')['Weighted Avg'].max().reset_index()
grouped_data_min = data.groupby('Hour')['Weighted Avg'].min().reset_index()
grouped_data_std = data.groupby('Hour')['Weighted Avg'].std().reset_index()

grouped_data_avg.rename(columns={'Weighted Avg': 'Average'}, inplace=True)
grouped_data_max.rename(columns={'Weighted Avg': 'Maximum'}, inplace=True)
grouped_data_min.rename(columns={'Weighted Avg': 'Minimum'}, inplace=True)
grouped_data_std.rename(columns={'Weighted Avg': 'Standard Deviation'}, inplace=True)

# Calculate moving averages using a window of 5
grouped_data_avg['Moving Average'] = grouped_data_avg['Average'].rolling(window=5).mean()
grouped_data_max['Moving Average'] = grouped_data_max['Maximum'].rolling(window=5).mean()
grouped_data_min['Moving Average'] = grouped_data_min['Minimum'].rolling(window=5).mean()
grouped_data_std['Moving Average'] = grouped_data_std['Standard Deviation'].rolling(window=5).mean()

# plt.plot(grouped_data_avg['Hour'], grouped_data_avg['Average'], label='Average')
# plt.plot(grouped_data_max['Hour'], grouped_data_max['Maximum'], label='Maximum')
# plt.plot(grouped_data_min['Hour'], grouped_data_min['Minimum'], label='Minimum')
# plt.plot(grouped_data_std['Hour'], grouped_data_std['Standard Deviation'], label='Standard Deviation')

plt.plot(grouped_data_avg['Hour'], grouped_data_avg['Moving Average'], label='Moving Average (Average)')
plt.plot(grouped_data_max['Hour'], grouped_data_max['Moving Average'], label='Moving Average (Maximum)')
plt.plot(grouped_data_min['Hour'], grouped_data_min['Moving Average'], label='Moving Average (Minimum)')
plt.plot(grouped_data_std['Hour'], grouped_data_std['Moving Average'], label='Moving Average (Standard Deviation)')

grouped_data_avg.rename(columns={'Moving Average': 'Moving Average (Average)'}, inplace=True)
grouped_data_max.rename(columns={'Moving Average': 'Moving Average (Maximum)'}, inplace=True)
grouped_data_min.rename(columns={'Moving Average': 'Moving Average (Minimum)'}, inplace=True)
grouped_data_std.rename(columns={'Moving Average': 'Moving Average (Standard Deviation)'}, inplace=True)

plt.xlabel('Hour')
plt.ylabel('Height')
plt.title(f'Statistics for Month {unique_months}')
plt.legend()

plt.show()
output_data = pd.concat([grouped_data_avg, grouped_data_max, grouped_data_min, grouped_data_std], axis=1)

output_file_path = 'output_data.txt'
output_data.to_csv(output_file_path, sep='\t', index=False) 
print(f"Data saved to '{output_file_path}'") 


# import pandas as pd
# import matplotlib.pyplot as plt

# data = pd.read_csv(output_file_path, delimiter=',')
# data['UTC Timestamp'] = pd.to_datetime(data['UTC Timestamp'])

# # Extract month and hour from the 'UTC Timestamp' column
# data['Month'] = data['UTC Timestamp'].dt.month
# data['Hour'] = data['UTC Timestamp'].dt.hour
# data['Hour'] = data['Hour'].apply(lambda x: f'{x:02d}:00')

# # Group by month and hour, and calculate the required statistics
# grouped_data = data.groupby(['Month', 'Hour'])['Weighted Avg'].agg(['mean', 'max', 'min', 'std']).reset_index()

# # Create subplots for each month
# unique_months = grouped_data['Month'].unique()

# for month in unique_months:
#     month_data = grouped_data[grouped_data['Month'] == month]

#     plt.figure(figsize=(10, 6))
#     plt.plot(month_data['Hour'], month_data['mean'], label='Average')
#     plt.plot(month_data['Hour'], month_data['max'], label='Maximum')
#     plt.plot(month_data['Hour'], month_data['min'], label='Minimum')
#     plt.plot(month_data['Hour'], month_data['std'], label='Standard Deviation')

#     plt.xlabel('Hour')
#     plt.ylabel('Height')
#     plt.title(f'Statistics for Month {month}')
#     plt.legend()
#     plt.grid()

#     plt.show()
