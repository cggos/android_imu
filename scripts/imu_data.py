#!/usr/bin/env python
# coding=utf-8

##########################################################################################
# If your phone has not all these sensors, only the available sensor data is transmitted.

# Example UDP packet:
# 890.71558, 3, 0.076, 9.809, 0.565, 4, -0.559, 0.032, -0.134, 5, -21.660,-36.960,-28.140

# Timestamp [sec], sensorid, x, y, z, sensorid, x, y, z, sensorid, x, y, z

# Sensor id:
# 3 - Accelerometer (m/s^2)
# 4 - Gyroscope (rad/s)
# 5 - Magnetometer (micro-Tesla uT)
##########################################################################################

import socket
import traceback

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Imu


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


host = '192.168.1.105'
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))

# while 1:
#     try:
#         message, address = s.recvfrom(8192)
#         print (message)
#     except (KeyboardInterrupt, SystemExit):
#         raise
#     except:
#         traceback.print_exc()


def talker():
    pub = rospy.Publisher('chatter', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10)  # 10hz
    while not rospy.is_shutdown():
        hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()


def pub_imu():
    pub = rospy.Publisher('/android_imu/imu/data_raw', Imu, queue_size=10)
    rospy.init_node('pub_imu', anonymous=True)
    while not rospy.is_shutdown():
        try:
            message, address = s.recvfrom(8192)
            print (message)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            traceback.print_exc()
        # imu_str = "890.71558, 3,  0.076, 9.809, 0.565, 4,  -0.559, 0.032, -0.134,  5, -21.660,-36.960,-28.140"
        imu_data = message.split(",")
        imu_length = len(imu_data)
        if imu_length < 9:
            error_str = "imu data received is incomplete, its length is %d" % imu_length
            print(bcolors.FAIL + error_str + bcolors.ENDC)
            continue
        time_stamp = imu_data[0].split(".")
        imu_msg = Imu()
        imu_msg.header.frame_id = 'android_imu'
        imu_msg.header.stamp.secs = int(time_stamp[0])
        imu_msg.header.stamp.nsecs = float("0." + time_stamp[1]) * 1e9
        imu_msg.linear_acceleration.x = float(imu_data[2])
        imu_msg.linear_acceleration.y = float(imu_data[3])
        imu_msg.linear_acceleration.z = float(imu_data[4])
        imu_msg.angular_velocity.x = float(imu_data[6])
        imu_msg.angular_velocity.y = float(imu_data[7])
        imu_msg.angular_velocity.z = float(imu_data[8])
        pub.publish(imu_msg)


def main(_):
    try:
        rospy.loginfo("=== start receive and publish imu data ===")
        pub_imu()
    except rospy.ROSInterruptException:
        pass


if __name__ == '__main__':
    main('_')
