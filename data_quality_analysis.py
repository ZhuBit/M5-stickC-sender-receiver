import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import numpy as np
def load_csv_files(name):
    # Construct file paths
    right_file_path = f'data/{name}_R.csv'
    left_file_path = f'data/{name}_L.csv'

    # Function to process each file
    def process_file(file_path):
        data_list = []
        current_row = []
        with open(file_path, mode='r', encoding='utf-8') as file:
            next(file)  # Skip the header
            for line in file:
                # Check if the line starts with 'S'
                if line.strip().startswith("S"):
                    if current_row:
                        # Ensure the row has 10 items
                        while len(current_row) < 10:
                            current_row.append('NaN')
                        # Add the completed row to data_list
                        data_list.append(current_row)
                        current_row = []
                # Split the line by commas and extend the current row
                current_row.extend(line.strip().split(','))
            # Ensure the last row has 10 items
            if current_row:
                while len(current_row) < 10:
                    current_row.append('NaN')
                data_list.append(current_row)
        return data_list

    # Load the files into lists
    try:
        right_df = process_file(right_file_path)
        left_df = process_file(left_file_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None, None

    return right_df, left_df


def create_count_plots_per_second(left_df, right_df, file_name):
    # Function to calculate the 1-second interval for a timestamp
    def calculate_interval(timestamp):
        return timestamp // 1000  # 1000 milliseconds = 1 second

    # Function to count items in each interval
    def count_intervals(data):
        interval_counts = {}
        for row in data:
            try:
                timestamp = int(row[-1])  # Assuming the timestamp is the last item
                interval = calculate_interval(timestamp)
                interval_counts[interval] = interval_counts.get(interval, 0) + 1
            except ValueError:
                continue  # Skip rows with invalid data
        return interval_counts

    # Count the intervals for left and right data
    left_counts = count_intervals(left_df)
    right_counts = count_intervals(right_df)

    # Plotting the counts
    plt.figure(figsize=(12, 5))

    # Left data plot
    plt.subplot(1, 2, 1)
    plt.bar(left_counts.keys(), left_counts.values())
    plt.title("Left Data Interval Counts (Per Second)")
    plt.xlabel("1-Second Intervals")
    plt.ylabel("Count")

    # Right data plot
    plt.subplot(1, 2, 2)
    plt.bar(right_counts.keys(), right_counts.values())
    plt.title("Right Data Interval Counts (Per Second)")
    plt.xlabel("1-Second Intervals")
    plt.ylabel("Count")

    plt.tight_layout()
    #plt.show()
    plt.savefig(f'results/{file_name}_countplot.png')




import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_time_series_and_distribution_plots_with_stats(left_df, right_df, file_name):
    # Function to calculate the 1-second interval for a timestamp
    def calculate_interval(timestamp):
        return timestamp // 1000  # 1000 milliseconds = 1 second

    # Function to count items in each interval
    def count_intervals(data, index=-1):
        interval_counts = {}
        for row in data:
            try:
                timestamp = int(row[index])  # Use specified index for timestamp
                interval = calculate_interval(timestamp)
                interval_counts[interval] = interval_counts.get(interval, 0) + 1
            except ValueError:
                continue  # Skip rows with invalid data
        return interval_counts

    # Function to get stats from frequency data
    def get_stats(freq_data):
        sorted_freqs = sorted(freq_data)
        lowest_5 = sorted_freqs[:5]
        top_5 = sorted_freqs[-5:]
        avg_freq = np.mean(sorted_freqs)
        return lowest_5, avg_freq, top_5

    # Function to add stats to plot
    def add_stats_to_plot(ax, stats, title):
        lowest_5, avg_freq, top_5 = stats
        textstr = f'{title}\nLowest 5 Freqs: {lowest_5}\nAverage Freq: {avg_freq:.2f}\nTop 5 Freqs: {top_5}'
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle="round", alpha=0.5))

    # Function to create a distribution plot
    def distribution_plot(ax, data, title):
        frequencies, counts = np.unique(data, return_counts=True)
        ax.bar(frequencies, counts)
        ax.set_title(title)
        ax.set_xlabel("Number of Samples per Interval")
        ax.set_ylabel("Frequency")

    # Plotting
    fig, axs = plt.subplots(4, 2, figsize=(12, 20))

    # Count intervals and get stats for original and new requirement
    for i, index in enumerate([-1, -2]):
        left_counts = count_intervals(left_df, index)
        right_counts = count_intervals(right_df, index)

        left_stats = get_stats(list(left_counts.values()))
        right_stats = get_stats(list(right_counts.values()))
        if index == -1:
            label = "Saved Timestamp"
        else:
            label = "Received Timestamp"
        # Time series plots
        axs[i*2, 0].plot(list(left_counts.keys()), list(left_counts.values()))
        axs[i*2, 0].set_title(f"Left Data Time Series ( {label})")
        axs[i*2, 0].set_xlabel("Time (1-Second Intervals)")
        axs[i*2, 0].set_ylabel("Frequency")

        axs[i*2, 1].plot(list(right_counts.keys()), list(right_counts.values()))
        axs[i*2, 1].set_title(f"Right Data Time Series ({label})")
        axs[i*2, 1].set_xlabel("Time (1-Second Intervals)")
        axs[i*2, 1].set_ylabel("Frequency")

        # Distribution plots
        distribution_plot(axs[i*2 + 1, 0], list(left_counts.values()), f"Left Data Distribution (index {index})")
        add_stats_to_plot(axs[i*2 + 1, 0], left_stats, "Left Hand Stats")

        distribution_plot(axs[i*2 + 1, 1], list(right_counts.values()), f"Right Data Distribution (index {index})")
        add_stats_to_plot(axs[i*2 + 1, 1], right_stats, "Right Hand Stats")

    plt.tight_layout()
    plt.savefig(f'results/{file_name}.png')

# Example usage
file_name = "stefantest1"
right, left = load_csv_files(file_name)
create_time_series_and_distribution_plots_with_stats(left, right, file_name)