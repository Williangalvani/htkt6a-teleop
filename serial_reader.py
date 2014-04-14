#
# Serial protocol for channel data from Hobby King HK-T6A v2 6-channel 2.4GHz transmitter
# Frame structure obtained from: https://github.com/minghuascode/SampleCode/blob/master/rcprogram/t6src/bin/helico/src/mainwindowimpl.cpp
#
# Baud rate 115200 8N1
# Frame: 0x55 0xFC 1HI 1LO 2HI 2LO 3HI 3LO 4HI 4LO 5HI 5LO 6HI 6LO 7HI 7LO 8HI 8LO
#

import serial
import threading

PITCH = 1
ROLL = 0
YAW = 3
THROTTLE = 2
SENSIBILITY = 0.005

 
class Reader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.channels_permanent = [0,0,0,0,0,0,0,0]
        self.channels = [0,0,0,0,0,0,0,0]
        self.quit = False
 
    def run(self):
	ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
        )
	print ser
        #ser.open()
        ser.isOpen()
        channel = 0
        state = 0
        while not self.quit:
            c = ord(ser.read(1))
            if state == 0 and c == 0x55:
                state = 1
                # print "s1"
                self.channels = []

            elif state == 1 and c == 0xFC:
                # print "s2"
                state = 2

            elif state == 2:
                channel = c * 255
                # print "s3"
                state = 3
            elif state == 3:
                channel += c
                self.channels.append(channel)
                if (len(self.channels) == 8):
                    #print "chan: " + " ".join(["%05u" % chan for chan in channels])
                    chan_scaled = map(lambda chan: int((chan - 1500)), self.channels)
                    self.channels_permanent = chan_scaled
                    #chan_scaled = map(lambda chan: int((chan - 1500) * 32.768), channels)
                    #chan_scaled = map(lambda chan: (chan & 0xFF00) >> 8 | (chan & 0x00FF) << 8, chan_scaled)
                    #print "scal: " + " ".join(["%05u" % chan for chan in chan_scaled])

                    # print "s0"
                    state = 0
                else:
                    # print "s2"
                    state = 2
            else:
                print "no frame" + " %02x" % c
                state = 0

    def getCoords(self):
        linear = (self.channels_permanent[PITCH]*SENSIBILITY,
                  -self.channels_permanent[ROLL]*SENSIBILITY,
                  self.channels_permanent[THROTTLE]*SENSIBILITY*0.1
                  )
        angular = (0,0,-self.channels_permanent[YAW]*SENSIBILITY)
        return linear , angular
 
if __name__ == "__main__":
    a = Reader()
    a.start()
