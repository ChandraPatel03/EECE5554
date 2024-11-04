import pandas as pa
import numpy as nu
import datetime
import rosbag
import matplotlib.pyplot as mpl

def load_rosbag(bag_path, topic):
    bag = rosbag.Bag(bag_path)

    data = {
        'timestamp': [],
        'latitude': [],
        'longitude': [],
        'altitude': [],
        'easting': [],
        'northing': []
    }

    for _, msg, t in bag.read_messages(topics=[topic]):
        data['timestamp'].append(t.to_sec())
        data['latitude'].append(msg.latitude)
        data['longitude'].append(msg.longitude)
        data['altitude'].append(msg.altitude)
        data['easting'].append(msg.utm_easting)
        data['northing'].append(msg.utm_northing)

    bag.close()

    return pa.DataFrame(data)

def analyze_stationary_data(open_df, occluded_df):
    # Convert timestamp to datetime for Open data
    open_df['timestamp'] = open_df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    open_df['timestamp'] = pa.to_datetime(open_df['timestamp'])

    # Convert timestamp to datetime for Occluded data
    occluded_df['timestamp'] = occluded_df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    occluded_df['timestamp'] = pa.to_datetime(occluded_df['timestamp'])

    # Convert columns to NumPy arrays
    open_easting = open_df['easting'].to_numpy()
    open_northing = open_df['northing'].to_numpy()
    open_altitude = open_df['altitude'].to_numpy()

    occluded_easting = occluded_df['easting'].to_numpy()
    occluded_northing = occluded_df['northing'].to_numpy()
    occluded_altitude = occluded_df['altitude'].to_numpy()

    # Subtracting the offset
    open_easting -= open_easting[0]
    open_northing -= open_northing[0]
    occluded_easting -= occluded_easting[0]
    occluded_northing -= occluded_northing[0]

    # Calculate centroids for Open data
    open_centroid = {
        'easting': nu.mean(open_easting),
        'northing': nu.mean(open_northing)
    }

    # Calculate centroids for Occluded data
    occluded_centroid = {
        'easting': nu.mean(occluded_easting),
        'northing': nu.mean(occluded_northing)
    }

    # Print centroid coordinates
    print("Open Spot Centroid Coordinates: Easting = {:.2f} meters, Northing = {:.2f} meters".format(open_centroid['easting'], open_centroid['northing']))
    print("Occluded Spot Centroid Coordinates: Easting = {:.2f} meters, Northing = {:.2f} meters".format(occluded_centroid['easting'], occluded_centroid['northing']))

    # Convert timestamp to elapsed seconds for Open data
    open_start_time = open_df['timestamp'].iloc[0]
    open_df['elapsed_time'] = (open_df['timestamp'] - open_start_time).dt.total_seconds()

    # Convert timestamp to elapsed seconds for Occluded data
    occluded_start_time = occluded_df['timestamp'].iloc[0]
    occluded_df['elapsed_time'] = (occluded_df['timestamp'] - occluded_start_time).dt.total_seconds()

    # Convert elapsed_time and altitude to NumPy arrays for plotting
    elapsed_time_open = open_df['elapsed_time'].to_numpy()
    elapsed_time_occluded = occluded_df['elapsed_time'].to_numpy()

    # Ensure the altitude arrays are also NumPy arrays
    open_altitude = open_df['altitude'].to_numpy()
    occluded_altitude = occluded_df['altitude'].to_numpy()

    # Plot altitude vs. elapsed time for both Open and Occluded data
    mpl.figure()
    mpl.plot(elapsed_time_open, open_altitude, label='Open Spot', marker='o', color='blue')
    mpl.plot(elapsed_time_occluded, occluded_altitude, label='Occluded Spot', marker='x', color='red')
    mpl.title('Stationary Altitude vs. Time Plot')
    mpl.xlabel('Elapsed Time (seconds)')
    mpl.ylabel('Altitude (meters)')
    mpl.legend()

    # Plot northing vs. easting scatterplots for both Open and Occluded data
    mpl.figure()
    mpl.scatter(open_easting, open_northing, label='Open Spot', marker='o', color='blue')
    mpl.scatter(occluded_easting, occluded_northing, label='Occluded Spot', marker='o', color='red')
    mpl.scatter(open_centroid['easting'], open_centroid['northing'], label='Open Centroid', marker='x', color='green')
    mpl.scatter(occluded_centroid['easting'], occluded_centroid['northing'], label='Occluded Centroid', marker='x', color='orange')
    mpl.title('Northing vs. Easting Scatterplots')
    mpl.xlabel('Easting (meters)')
    mpl.ylabel('Northing (meters)')
    mpl.legend()

    # Calculate Euclidean distance from each point to the centroid for Open data
    open_distances = nu.sqrt((open_easting - open_centroid['easting'])**2 + (open_northing - open_centroid['northing'])**2)

    # Calculate Euclidean distance from each point to the centroid for Occluded data
    occluded_distances = nu.sqrt((occluded_easting - occluded_centroid['easting'])**2 + (occluded_northing - occluded_centroid['northing'])**2)

    # Print mean errors
    distance1 = nu.mean(open_distances)
    distance2 = nu.mean(occluded_distances)
    print("Error for Open data (mean distance from centroid):", distance1)
    print("Error for Occluded data (mean distance from centroid):", distance2)

    # Plot histogram of distances for Open Spot
    mpl.figure()
    mpl.hist(open_distances, bins=20, alpha=0.7, label='Open Spot - Distance from Centroid', color='blue')
    mpl.title('Open Spot Distance from Centroid Histogram')
    mpl.xlabel('Distance (meters)')
    mpl.ylabel('Frequency (count)')
    mpl.legend()

    # Plot histogram of distances for Occluded Spot
    mpl.figure()
    mpl.hist(occluded_distances, bins=20, alpha=0.7, label='Occluded Spot - Distance from Centroid', color='red')
    mpl.title('Occluded Spot Distance from Centroid Histogram')
    mpl.xlabel('Distance (meters)')
    mpl.ylabel('Frequency (count)')
    mpl.legend()

if __name__ == '__main__':
    open_spot_df = load_rosbag('/home/chandra/EECE5554/lab2/data/Stat_open.bag', '/gps')
    occluded_spot_df = load_rosbag('/home/chandra/EECE5554/lab2/data/Square_occluded.bag', '/gps')

    # Analyze stationary data
    analyze_stationary_data(open_spot_df, occluded_spot_df)

    # Show the plots
    mpl.show()
