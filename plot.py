import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Read the dataset into a Pandas DataFrame
df = pd.read_csv('statistics.csv')  # Replace 'statistics.csv' with the actual filename/path

# Convert the timestamp column to datetime format
df['Max Thickness Timestamp'] = pd.to_datetime(df['Max Thickness Timestamp'])

# Sort the DataFrame by timestamp
df = df.sort_values(by='Max Thickness Timestamp')

# Create the figure and axes
fig, ax = plt.subplots()

# Group the data by type: General, Day, Night
grouped_data = df.groupby('Type')

# Plot each group separately
for group_name, group_data in grouped_data:
    timestamp = group_data['Max Thickness Timestamp']
    thickness = group_data['Max Thickness']
    ax.plot(timestamp, thickness, marker='o', linestyle='-', label=group_name)

# Format the x-axis tick labels
date_formatter = DateFormatter('%d-%m-%Y %H:%M:%S')
ax.xaxis.set_major_formatter(date_formatter)
plt.xticks(rotation=45)

# Set the x-axis and y-axis labels
ax.set_xlabel('Timestamp')
ax.set_ylabel('Thickness')

# Set the title
ax.set_title('Thickness Data')

# Display the legend
ax.legend()

# Adjust the spacing
plt.tight_layout()

# Show the plot
plt.show()
