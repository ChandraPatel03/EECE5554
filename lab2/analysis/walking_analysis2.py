import pandas as pa
import numpy as nu
import datetime
import rosbag
import matplotlib.pyplot as mpl

def load_rosbag(bag_path, topic):
    bag = rosbag.Bag(bag_path)

    data = {'timestamp': [], 'latitude': [], 'longitude': [], 'altitude': [], 'easting': [], 'northing': []}

    for _, msg, t in bag.read_messages(topics=[topic]):
        data['timestamp'].append(t.to_sec())
        data['latitude'].append(msg.latitude)
        data['longitude'].append(msg.longitude)
        data['altitude'].append(msg.altitude)
        data['easting'].append(msg.utm_easting)
        data['northing'].append(msg.utm_northing)

    bag.close()

    return pa.DataFrame(data)

def analyze_walking_data(walking_df):
    # Convert timestamp to datetime format
    walking_df['timestamp'] = walking_df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    walking_df['timestamp'] = pa.to_datetime(walking_df['timestamp'])

    # Convert columns to NumPy arrays
    walking_easting = walking_df['easting'].to_numpy()
    walking_northing = walking_df['northing'].to_numpy()
    walking_altitude = walking_df['altitude'].to_numpy()

    # Subtract the offset
    walking_easting -= walking_easting[0]
    walking_northing -= walking_northing[0]

    # Calculate centroids for Walking data
    walking_centroid = {
        'easting': nu.mean(walking_easting),
        'northing': nu.mean(walking_northing)
    }

    # Calculate standard deviation for Walking data
    walking_std_easting = nu.std(walking_easting)
    walking_std_northing = nu.std(walking_northing)

    # Plot northing vs. easting scatterplots for Walking data with a best-fit line
    mpl.figure(figsize=(10, 6))
    mpl.scatter(walking_easting, walking_northing, label='Walking', marker='o', color='blue', alpha=0.7)
    #mpl.scatter(walking_centroid['easting'], walking_centroid['northing'], label='Walking Centroid', marker='x', color='green', s=100)
    
    # Calculate and plot the best-fit line
    slope, intercept = nu.polyfit(walking_easting, walking_northing, 1)
    best_fit_line = slope * walking_easting + intercept
    mpl.plot(walking_easting, best_fit_line, color='red', linestyle='--', linewidth=2, label='Best Fit Line')

    mpl.title(f'Walking Northing vs. Easting Scatterplot (StdDev = {walking_std_easting:.2f}, {walking_std_northing:.2f})')
    mpl.xlabel('Easting (meters)')
    mpl.ylabel('Northing (meters)')
    mpl.legend()
    mpl.grid(True)

    # Plot altitude vs. time plot for Walking data
    mpl.figure(figsize=(10, 6))
    mpl.plot(walking_df['timestamp'].values, walking_altitude, label='Walking', marker='o', color='blue', alpha=0.7)
    mpl.title('Walking Altitude vs. Time Plot')
    mpl.xlabel('Timestamp(Date hr:min)')
    mpl.ylabel('Altitude (meters)')
    mpl.legend()
    mpl.grid(True)

    # Calculate Euclidean distance from each point to the centroid for Walking data
    walking_distances = nu.sqrt((walking_easting - walking_centroid['easting'])**2 + (walking_northing - walking_centroid['northing'])**2)

    # Print mean errors
    #walking_distance = nu.mean(walking_distances)
    #print("Error for Walking data:", walking_distance)

if __name__ == '__main__':
    walking_df = load_rosbag('/home/chandra/EECE5554/lab2/data/square_open_area.bag', '/gps')

    # Analyze walking data
    analyze_walking_data(walking_df)

    # Show the plots
    mpl.show()
