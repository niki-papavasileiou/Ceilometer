import matplotlib.pyplot as plt
import pandas as pd
import os
import ast
import re 

folder_path = r"C:\Users\nikip\Desktop\testceilo"
folder_path_out = r"C:\Users\nikip\Desktop\results"

def calculate_weighted_avg(df):
    weights = [1, 2, 3]
    numeric_cols = ['Mixing Layer 1( Meters )', 'Mixing Layer 2( Meters )', 'Mixing Layer 3( Meters )']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    avg = sum(df[col] * weight for col, weight in zip(numeric_cols, weights))
    return avg / sum(weights)

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
        df['Weighted Avg'] = calculate_weighted_avg(df)

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

# Iterate over the rows of the 'Sky Condition 2( Oktas ) Distribution' column
for index, row in enumerate(df_s['Sky Condition 1( Oktas ) Distribution']):
    # Convert the string representation of the dictionary to an actual dictionary
    dictionary_data = ast.literal_eval(row)
    
    # Extract the value corresponding to key 0 from the dictionary in each row
    value_at_0 = dictionary_data.get(0, 0)  # If key 0 doesn't exist, return 0 as default value
    
    if value_at_0 > 90:
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

data = pd.read_csv(output_file_path, delimiter=',')
data['UTC Timestamp'] = pd.to_datetime(data['UTC Timestamp'])

# Extract the hour from the 'UTC Timestamp' column
data['Hour'] = data['UTC Timestamp'].dt.hour
data['Hour'] = data['Hour'].apply(lambda x: f'{x:02d}:00')

# Group by hour, and calculate the average of the 'Weighted Avg' column
grouped_data_avg = data.groupby('Hour')['Weighted Avg'].mean().reset_index()
grouped_data_max = data.groupby('Hour')['Weighted Avg'].max().reset_index()
grouped_data_min = data.groupby('Hour')['Weighted Avg'].min().reset_index()
grouped_data_std = data.groupby('Hour')['Weighted Avg'].std().reset_index()

plt.plot(grouped_data_avg['Hour'], grouped_data_avg['Weighted Avg'], label='Average')

plt.plot(grouped_data_max['Hour'], grouped_data_max['Weighted Avg'], label='Maximum')

plt.plot(grouped_data_min['Hour'], grouped_data_min['Weighted Avg'], label='Minimum')

plt.plot(grouped_data_std['Hour'], grouped_data_std['Weighted Avg'], label='Standard Deviation')

plt.xlabel('Hour')
plt.ylabel('Weighted Avg')
plt.legend()

plt.show()
