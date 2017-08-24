#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Author: xxx xxx <xxx@xxx.xxx>
# Date:   xx.xx.xx
#-------------------------------------------------------------------------------

"""
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.
"""

#pylint: disable=fixme

import math

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane
#from styx_msgs.msg import Waypoint
#from styx_msgs.msg import TrafficLight

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number

def distance(waypoints, p1, p2):
    """ Get total distance between two waypoints given their index"""
    gap = 0
    euclidean_distance = lambda a, b: math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2  + (a.z - b.z)**2)

    for i in range(p1, p2+1):
        a = waypoints[p1].pose.pose.position
        b = waypoints[i].pose.pose.position
        gap += euclidean_distance(a, b)
        p1 = i
    return gap


def get_square_gap(a, b):
    """Returns squared euclidean distance between two 2D points"""
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy


def get_closest_waypoint_index(my_position, waypoints):
    """
    position: geometry_msg.msgs.Pose instance
    waypoints: list of styx_msgs.msg.Waypoint instances
    returns index of the closest waypoint in the list waypoints
    """
    best_gap = 1000000000000000000000000000000.0 # Really big number
    best_index = 0

    for i, waypoint in enumerate(waypoints):

        other_position = waypoint.pose.pose.position
        gap = get_square_gap(my_position, other_position)
        #TODO: should we use something similar to distance() instead of get_square_gap() instead?

        if gap < best_gap:
            best_index, best_gap = i, gap

    return best_index


def get_next_waypoints(waypoints, i, n):
    """Returns a list of n waypoints ahead of the vehicle"""
    m = min(len(waypoints), i + n)
    return waypoints[i:m]


def make_lane_object(frame_id, waypoints):
    """Lane object contains the list of final waypoints ahead with velocity"""
    lane = Lane()
    lane.header.frame_id = frame_id
    lane.waypoints = waypoints
    lane.header.stamp = rospy.Time.now()
    return lane

def get_waypoint_velocity(waypoint):
    """Get velocity of a given waypoints"""
    return waypoint.twist.twist.linear.x

def set_waypoint_velocity(waypoint, velocity):
    """sets the velocity of a given waypoint"""
    waypoint.twist.twist.linear.x = velocity


class WaypointUpdater(object):
    """Given the position and map this object returns
       points with target velocities representing path ahead"""

    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.base_waypoints_cb)
        #rospy.Subscriber('/obstacle_waypoints', PoseStamped, self.obstacle_cb)
        #rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)

        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # Current location (x,y) of the vehicle
        self.position = None

        # Current list of base waypoints from Lane object
        self.base_waypoints = None

        rospy.loginfo('WaypointUpdater Initialized.')
        rospy.spin()

    def pose_cb(self, msg):
        """ Publishes waypoints with target velocities whenever the vehicle location is received"""
        rospy.loginfo('WaypointUpdater: Current Pose received.')

        # store location (x, y)
        self.position = msg.pose.position
        frame_id = msg.header.frame_id

        if self.base_waypoints:

            # get closest waypoint
            index = get_closest_waypoint_index(self.position, self.base_waypoints)

            # make list of n waypoints ahead of vehicle
            lookahead_waypoints = get_next_waypoints(self.base_waypoints, index, LOOKAHEAD_WPS)

            # set velocity of all waypoints
            for waypoint in lookahead_waypoints:
                waypoint.twist.twist.linear.x = 4.47 #10mph in meters per second

            # make lane data structure to be published
            lane = make_lane_object(frame_id, lookahead_waypoints)

            # publish the subset of waypoints ahead
            self.final_waypoints_pub.publish(lane)

    def base_waypoints_cb(self, msg):
        """We store the given map """
        #msg: styx_msgs.msg.lane
        rospy.loginfo('WaypointUpdater: base waypoints received')
        self.base_waypoints = msg.waypoints

    def traffic_cb(self, msg):
        #pylint: disable=no-self-use
        "Consider traffic light when setting waypoint velocity"
        rospy.loginfo('WaypointUpdater: traffic waypoint received')

    def obstacle_cb(self, msg):
        #pylint: disable=no-self-use
        "Consider obstacles when setting waypoint velocity"
        rospy.loginfo('WaypointUpdater: obstacle waypoints received')
        # Consider obstacles when setting waypoint velocity


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
