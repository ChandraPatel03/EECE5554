project(gps_driver)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  message_generation
)

#Declare ROS messages, services and actions

## Generate messages in the 'msg' folder
add_message_files(
  FILES
  Customgps.msg
  # Message2.msg
)

## Generate added messages and services with any dependencies listed here
generate_messages(
  DEPENDENCIES
  std_msgs
)
