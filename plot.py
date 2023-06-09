import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Read the dataset into a Pandas DataFrame
df = pd.read_csv('statistics.csv')  

df['Max Thickness Timestamp'] = pd.to_datetime(df['Max Thickness Timestamp'])

df = df.sort_values(by='Max Thickness Timestamp')

fig, ax = plt.subplots()

# Group the data by type: General, Day, Night
grouped_data = df.groupby('Type')

for group_name, group_data in grouped_data:
    timestamp = group_data['Max Thickness Timestamp']
    max_thickness = group_data['Max Thickness']
    min_thickness = group_data['Min Thickness']
    avg_thickness = group_data['Average Thickness']
    ax.plot(timestamp, max_thickness, marker='o', linestyle='-', label=f'{group_name} (Max)')
    ax.plot(timestamp, min_thickness, marker='o', linestyle='-', label=f'{group_name} (Min)')
    ax.plot(timestamp, avg_thickness, marker='o', linestyle='-', label=f'{group_name} (Avg)')

# Format the x-axis tick labels
date_formatter = DateFormatter('%d-%m-%Y %H:%M:%S')
ax.xaxis.set_major_formatter(date_formatter)
plt.xticks(rotation=45)

ax.set_xlabel('Timestamp')
ax.set_ylabel('Thickness')

ax.set_title('Thickness Data')

ax.legend()

# plt.tight_layout()

plt.show()
