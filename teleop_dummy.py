#!/usr/bin/env python
import roslib;# roslib.load_manifest('drone_teleop')
import rospy

from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import sys, select, termios, tty

from serial_reader import Reader
import time



msg = """
Reading from the keyboard  and Publishing to Twist!
---------------------------
up/down:       move forward/backward
left/right:    move left/right
w/s:           increase/decrease altitude
a/d:           turn left/right
t/l:           takeoff/land
r:             reset (toggle emergency state)
anything else: stop

please don't have caps lock on.
CTRL+c to quit
"""




def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        ch = None
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def isData():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def getKey():
    if isData():
        return sys.stdin.read(1)
    else:
        return None


move_bindings = {
        68:('linear', 'y', 0.1), #left
        67:('linear', 'y', -0.1), #right
        65:('linear', 'x', 0.1), #forward
        66:('linear', 'x', -0.1), #back
        'w':('linear', 'z', 0.1),
        's':('linear', 'z', -0.1),
        'a':('angular', 'z', 1),
        'd':('angular', 'z', -1),
           }



quit = False
if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)
    print msg
    
    
    ppmReader = Reader()
    ppmReader.start()
    
    pub = rospy.Publisher('cmd_vel', Twist)
    land_pub = rospy.Publisher('/ardrone/land', Empty)
    reset_pub = rospy.Publisher('/ardrone/reset', Empty)
    takeoff_pub = rospy.Publisher('/ardrone/takeoff', Empty)

    rospy.init_node('drone_teleop')

    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            time.sleep(0.05)
            key = getKey()
            if key and key != None:
                print key
                # takeoff and landing
                if key == 'l':
                    pass#land_pub.publish(Empty())
                if key == 'r':
                    pass#reset_pub.publish(Empty())
                if key == 't':
                    pass#takeoff_pub.publish(Empty())
                try:
                    if ord(key) == 27:
                        key = getKey()
                        key = getKey()
                    #twist = Twist()
                    if ord(key) in move_bindings.keys():
                        key = ord(key)
                    if key in move_bindings.keys():
                        (lin_ang, xyz, speed) = move_bindings[key]
                        print move_bindings[key]
                        #setattr(getattr(twist, lin_ang), xyz, speed)
                except:
                    pass
                if (key == 'x'):
                    print "breaking the law"
                    ppmReader.quit = True
                    break
            #else:
                
            twist = Twist()
            linear,angular = ppmReader.getCoords()
            
            print linear, angular
            twist.linear.x = linear[0]
            twist.linear.y = linear[1]
            twist.linear.z = linear[2]
            
            twist.angular.x = angular[0]
            twist.angular.y = angular[1]
            twist.angular.z = angular[2]
            pub.publish(twist)  # talvez descomentar!
            #pub.publish(twist)

    except Exception as e:
        print e
        print repr(e)

    finally:
        
        #twist = Twist()
        #twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        #twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        
        #pub.publish(twist)
        
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
