import pandas as pd
import os 

folder_path = r"to path telospanton tu folder me ta data"  

# Get a list of all csv files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Sort the files based on modification time in descending order
csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)

if len(csv_files) < 2:
    print("There are not enough files in the directory.")
else:
    csv_file = csv_files[1]
    
    file_path = os.path.join(folder_path, csv_file)
    df = pd.read_csv(file_path, delimiter=',')
    print(csv_file)

df['UTC Timestamp'] = pd.to_datetime(df['UTC Timestamp'])
df['Hour'] = df['UTC Timestamp'].dt.hour
df['Mixing Layer 3( Meters )'] = pd.to_numeric(df['Mixing Layer 3( Meters )'], errors='coerce')
df['Mixing Layer 1( Meters )'] = pd.to_numeric(df['Mixing Layer 1( Meters )'], errors='coerce')
df.loc[:, 'Thickness'] = df['Mixing Layer 3( Meters )'] - df['Mixing Layer 1( Meters )']

night_df = df[df['Hour'] < 6].copy()  # Assuming night is from 12 AM to 6 AM
day_df = df[df['Hour'] >= 6].copy()


# -----------------------------GENERAL-------------------------------------
df.loc[:, 'Thickness'] = df['Mixing Layer 3( Meters )'] - df['Mixing Layer 1( Meters )']
max_diff_index = df['Thickness'].abs().idxmax()
min_diff_index = df['Thickness'].abs().idxmin()

timestamp = 'UTC Timestamp'
max_timestamp = df.loc[max_diff_index, timestamp]
min_timestamp = df.loc[min_diff_index, timestamp]

max_thickness = df['Thickness'].max()
min_thickness = df['Thickness'].min()

total_rows = len(df)
max_thickness_frequency = df['Thickness'].value_counts()[max_thickness]
min_thickness_frequency = df['Thickness'].value_counts()[min_thickness]

max_thickness_percentage = round((max_thickness_frequency / total_rows) * 100, 2)
min_thickness_percentage = round((min_thickness_frequency / total_rows) * 100, 2)

print("Maximum Thickness:", max_thickness, "Timestamp:", max_timestamp, "Frequency of Maximum Thickness:",
      max_thickness_percentage, "%")
print("Minimum Thickness:", min_thickness, "Timestamp:", min_timestamp, "Frequency of Minimum Thickness:",
      min_thickness_percentage, "%")

average_thickness = df['Thickness'].mean()
print("Average Thickness:", average_thickness)

percentage1 = df['Sky Condition 1( Oktas )'].value_counts(normalize=True) * 100
percentage2 = df['Sky Condition 2( Oktas )'].value_counts(normalize=True) * 100
percentage3 = df['Sky Condition 3( Oktas )'].value_counts(normalize=True) * 100
percentage4 = df['Sky Condition 4( Oktas )'].value_counts(normalize=True) * 100
percentage5 = df['Sky Condition 5( Oktas )'].value_counts(normalize=True) * 100

stats_dict = {
    'Type': 'General',
    'Max Thickness': max_thickness,
    'Max Thickness Timestamp': max_timestamp,
    'Max Thickness Frequency': max_thickness_percentage,
    'Min Thickness': min_thickness,
    'Min Thickness Timestamp': min_timestamp,
    'Min Thickness Frequency': min_thickness_percentage,
    'Average Thickness': average_thickness,
    'Sky Condition 1( Oktas ) Distribution': percentage1.to_dict(),
    'Sky Condition 2( Oktas ) Distribution': percentage2.to_dict(),
    'Sky Condition 3( Oktas ) Distribution': percentage3.to_dict(),
    'Sky Condition 4( Oktas ) Distribution': percentage4.to_dict(),
    'Sky Condition 5( Oktas ) Distribution': percentage5.to_dict(),
}

# Convert the dictionary into a DataFrame
stats_df = pd.DataFrame([stats_dict])


# ---------------------------------------------DAY---------------------------------------------------------

day_df.loc[:, 'Thickness'] = day_df['Mixing Layer 3( Meters )'] - day_df['Mixing Layer 1( Meters )']
max_diff_index = day_df['Thickness'].abs().idxmax()
min_diff_index = day_df['Thickness'].abs().idxmin()

max_timestamp = day_df.loc[max_diff_index, timestamp]
min_timestamp = day_df.loc[min_diff_index, timestamp]

max_thickness = day_df['Thickness'].max()
min_thickness = day_df['Thickness'].min()

total_rows = len(day_df)
max_thickness_frequency = day_df['Thickness'].value_counts()[max_thickness]
min_thickness_frequency = day_df['Thickness'].value_counts()[min_thickness]

max_thickness_percentage = round((max_thickness_frequency / total_rows) * 100, 2)
min_thickness_percentage = round((min_thickness_frequency / total_rows) * 100, 2)

print("(DAY) Maximum Thickness:", max_thickness, "Timestamp:", max_timestamp, "Frequency of Maximum Thickness:",
      max_thickness_percentage, "%")
print("(DAY) Minimum Thickness:", min_thickness, "Timestamp:", min_timestamp, "Frequency of Minimum Thickness:",
      min_thickness_percentage, "%")

average_thickness = day_df['Thickness'].mean()
print("(DAY) Average Thickness:", average_thickness)

percentage1 = day_df['Sky Condition 1( Oktas )'].value_counts(normalize=True) * 100
percentage2 = day_df['Sky Condition 2( Oktas )'].value_counts(normalize=True) * 100
percentage3 = day_df['Sky Condition 3( Oktas )'].value_counts(normalize=True) * 100
percentage4 = day_df['Sky Condition 4( Oktas )'].value_counts(normalize=True) * 100
percentage5 = day_df['Sky Condition 5( Oktas )'].value_counts(normalize=True) * 100

stats_dict.update({
    'Type': 'Day',
    'Max Thickness': max_thickness,
    'Max Thickness Timestamp': max_timestamp,
    'Max Thickness Frequency': max_thickness_percentage,
    'Min Thickness': min_thickness,
    'Min Thickness Timestamp': min_timestamp,
    'Min Thickness Frequency': min_thickness_percentage,
    'Average Thickness': average_thickness,
    'Sky Condition 1( Oktas ) Distribution': percentage1.to_dict(),
    'Sky Condition 2( Oktas ) Distribution': percentage2.to_dict(),
    'Sky Condition 3( Oktas ) Distribution': percentage3.to_dict(),
    'Sky Condition 4( Oktas ) Distribution': percentage4.to_dict(),
    'Sky Condition 5( Oktas ) Distribution': percentage5.to_dict(),
})

# Append the day statistics to the DataFrame
stats_df = pd.concat([stats_df, pd.DataFrame([stats_dict])], ignore_index=True)


# ---------------------------------------------NIGHT---------------------------------------------------------

night_df.loc[:, 'Thickness'] = night_df['Mixing Layer 3( Meters )'] - night_df['Mixing Layer 1( Meters )']
max_diff_index = night_df['Thickness'].abs().idxmax()
min_diff_index = night_df['Thickness'].abs().idxmin()

max_timestamp = night_df.loc[max_diff_index, timestamp]
min_timestamp = night_df.loc[min_diff_index, timestamp]

max_thickness = night_df['Thickness'].max()
min_thickness = night_df['Thickness'].min()

total_rows = len(night_df)
max_thickness_frequency = night_df['Thickness'].value_counts()[max_thickness]
min_thickness_frequency = night_df['Thickness'].value_counts()[min_thickness]

max_thickness_percentage = round((max_thickness_frequency / total_rows) * 100, 2)
min_thickness_percentage = round((min_thickness_frequency / total_rows) * 100, 2)

print("(NIGHT) Maximum Thickness:", max_thickness, "Timestamp:", max_timestamp, "Frequency of Maximum Thickness:",
      max_thickness_percentage, "%")
print("(NIGHT) Minimum Thickness:", min_thickness, "Timestamp:", min_timestamp, "Frequency of Minimum Thickness:",
      min_thickness_percentage, "%")

average_thickness = night_df['Thickness'].mean()
print("(NIGHT) Average Thickness:", average_thickness)

percentage1 = night_df['Sky Condition 1( Oktas )'].value_counts(normalize=True) * 100
percentage2 = night_df['Sky Condition 2( Oktas )'].value_counts(normalize=True) * 100
percentage3 = night_df['Sky Condition 3( Oktas )'].value_counts(normalize=True) * 100
percentage4 = night_df['Sky Condition 4( Oktas )'].value_counts(normalize=True) * 100
percentage5 = night_df['Sky Condition 5( Oktas )'].value_counts(normalize=True) * 100

stats_dict.update({
    'Type': 'Night',
    'Max Thickness': max_thickness,
    'Max Thickness Timestamp': max_timestamp,
    'Max Thickness Frequency': max_thickness_percentage,
    'Min Thickness': min_thickness,
    'Min Thickness Timestamp': min_timestamp,
    'Min Thickness Frequency': min_thickness_percentage,
    'Average Thickness': average_thickness,
    'Sky Condition 1( Oktas ) Distribution': percentage1.to_dict(),
    'Sky Condition 2( Oktas ) Distribution': percentage2.to_dict(),
    'Sky Condition 3( Oktas ) Distribution': percentage3.to_dict(),
    'Sky Condition 4( Oktas ) Distribution': percentage4.to_dict(),
    'Sky Condition 5( Oktas ) Distribution': percentage5.to_dict(),
})

# Append the night statistics to the DataFrame
stats_df = pd.concat([stats_df, pd.DataFrame([stats_dict])], ignore_index=True)

filename = 'statistics.csv'

if not os.path.isfile(filename):
    open(filename, 'w').close()

if os.path.isfile(filename) and os.path.getsize(filename) > 0:
      stats_df.to_csv(filename, mode='a', index=False, header=False)
else:
    stats_df.to_csv(filename, mode='w', index=False)
