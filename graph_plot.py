import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from services.database import Report

# Your data
# data = [
#     (1, '2025-07-21 22:23:05', None, None, 0),
#     (2, '2025-07-21 22:23:05', 19.38, 0.0, 1),
#     (3, '2025-07-21 22:25:24', 25.84, None, 1),
#     (4, '2025-07-21 22:26:45', 12.22, 11.11111111111111, 1),
#     (5, '2025-07-21 22:28:06', 27.83, 77.77777777777779, 3),
#     (6, '2025-07-21 22:29:27', 28.9, 0.0, 1),
#     (7, '2025-07-21 22:30:47', 38.85, 0.0, 1)
# ]
report = Report()
data = report.get_report_data()


# Parse the data
timestamps = []
facial_values = []
keystroke_values = []

for record in data:
    id_val, datetime_str, facial, keystroke, level = record
    
    # Parse datetime
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    timestamps.append(dt)
    
    # Handle None values - we'll use NaN for matplotlib to skip these points
    facial_values.append(facial if facial is not None else np.nan)
    keystroke_values.append(keystroke if keystroke is not None else np.nan)

# Create the plot - single graph
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

# Plot both metrics on the same graph with different colors
ax.plot(timestamps, facial_values, 'b-o', linewidth=2, markersize=6, label='Facial Expression', color='blue')
ax.plot(timestamps, keystroke_values, 'r-s', linewidth=2, markersize=6, label='Keystroke Dynamics', color='red')

ax.set_ylabel('Percentage (%)', fontsize=12)
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=12)
ax.set_title('Daily Keystroke Dynamics and Facial Expression Analysis - July 21, 2025', fontsize=14, pad=20)

# Format x-axis to show the full day
ax.set_xlabel('Time', fontsize=12)

# Set time format
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

# Set x-axis limits to show the whole day (00:00 to 23:59)
start_of_day = datetime(2025, 7, 21, 0, 0, 0)
end_of_day = datetime(2025, 7, 21, 23, 59, 59)
ax.set_xlim(start_of_day, end_of_day)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Add some styling
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add annotations for data points with values
for i, (ts, facial, keystroke) in enumerate(zip(timestamps, facial_values, keystroke_values)):
    if not np.isnan(facial):
        ax.annotate(f'{facial:.1f}%', (ts, facial), 
                   textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color='blue')
    if not np.isnan(keystroke):
        ax.annotate(f'{keystroke:.1f}%', (ts, keystroke), 
                   textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color='red')

plt.show()

# Print summary statistics
print("Data Summary:")
print("=============")
valid_facial = [f for f in facial_values if not np.isnan(f)]
valid_keystroke = [k for k in keystroke_values if not np.isnan(k)]

if valid_facial:
    print(f"Facial Expression - Min: {min(valid_facial):.2f}%, Max: {max(valid_facial):.2f}%, Avg: {np.mean(valid_facial):.2f}%")
if valid_keystroke:
    print(f"Keystroke Dynamics - Min: {min(valid_keystroke):.2f}%, Max: {max(valid_keystroke):.2f}%, Avg: {np.mean(valid_keystroke):.2f}%")

print(f"Total data points: {len(data)}")
print(f"Time range: {min(timestamps).strftime('%H:%M:%S')} - {max(timestamps).strftime('%H:%M:%S')}")