import rospy
import utm
import serial
import sys
from std_msgs.msg import Header
from gps_driver.msg import Customgps

def driver():
    try:
        # Initialize the ROS node
        pub = rospy.Publisher('gps', Customgps, queue_size=10)
        rospy.init_node('talker', anonymous=True)
        rospy.loginfo("GPS Driver node initialized.")
        
        # Create a message object
        msg = Customgps()
        
        # Get serial port parameters
        serial_port = rospy.get_param('~port', "/dev/ttyUSB0")
        serial_baud = rospy.get_param('~baudrate', 4800)
        rospy.loginfo(f"Connecting to serial port: {serial_port} with baud rate: {serial_baud}")
        
        try:
            ser = serial.Serial(serial_port, serial_baud, timeout=3)
            rospy.loginfo(f"Successfully connected to serial port: {serial_port}")
        except serial.SerialException as e:
            rospy.logerr(f"Failed to connect to serial port: {serial_port}. Error: {e}")
            sys.exit(1)  # Exit the script if the serial connection fails

        while not rospy.is_shutdown():
            try:
                # Read and decode GPS data from the serial port
                receive = ser.readline().decode('utf-8').strip()
                
                if "$GPGGA" in receive:
                    data = receive.split(",")
                    rospy.loginfo(f"Received GPGGA data: {data}")
                    
                    try:
                        # Extract UTC time and convert to ROS time format
                        utc = float(data[1])
                        utc_hrs = int(utc // 10000)
                        utc_mint = int((utc - (utc_hrs * 10000)) // 100)
                        utc_sec = (utc - (utc_hrs * 10000) - (utc_mint * 100))
                        utc_final_secs = (utc_hrs * 3600 + utc_mint * 60 + utc_sec)
                        utc_final_nsecs = int((utc_final_secs * (10 ** 7)) % (10 ** 7))
                        
                        # Latitude and Longitude conversion
                        lat = float(data[2])
                        lat_DD = int(lat / 100)
                        lat_mm1 = lat - (lat_DD * 100)
                        lat_converted = lat_DD + lat_mm1 / 60
                        if data[3] == 'S':
                            lat_converted = -lat_converted

                        long = float(data[4])
                        long_DD = int(long / 100)
                        long_mm1 = long - (long_DD * 100)
                        long_converted = long_DD + long_mm1 / 60
                        if data[5] == 'W':
                            long_converted = -long_converted

                        # Altitude
                        alt = float(data[9])

                        # UTM conversion
                        newlatlong = utm.from_latlon(lat_converted, long_converted)
                        rospy.loginfo(f'UTM Coordinates: Easting = {newlatlong[0]}, Northing = {newlatlong[1]}, Zone = {newlatlong[2]}, Letter = {newlatlong[3]}')

                        # Populate and publish message
                        msg.header.stamp.secs = int(utc_final_secs)
                        msg.header.stamp.nsecs = int(utc_final_nsecs)
                        msg.header.frame_id = 'GPS1_Frame'
                        msg.latitude = lat_converted
                        msg.longitude = long_converted
                        msg.altitude = alt
                        msg.utm_easting = newlatlong[0]
                        msg.utm_northing = newlatlong[1]
                        msg.zone = newlatlong[2]
                        msg.letter = newlatlong[3]
                        msg.hdop = float(data[8])
                        msg.gpgga_read = ','.join(data)
                        pub.publish(msg)

                    except (IndexError, ValueError) as e:
                        rospy.logwarn(f"Error processing GPS data: {data}. Error: {e}")
                        continue  # Skip this data if there's an issue
            except UnicodeDecodeError as e:
                rospy.logwarn(f"Failed to decode serial data: {e}")
                continue  # Skip if there's a decoding issue

    except rospy.ROSInterruptException:
        rospy.loginfo("ROS node interrupted before completion.")

    except Exception as e:
        rospy.logerr(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        driver()
    except Exception as e:
        rospy.logerr(f"Failed to run GPS driver: {e}")
