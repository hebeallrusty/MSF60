from machine import Pin
from MSF import *
import utime

# turn on the MSF60 module - this one has a P pin which requires logic low to start the pulses on pin T. sw is connected to pin P.
sw = Pin(1,Pin.OUT, Pin.PULL_DOWN)

# ti is connected to pin T. This is where the pulses are read from.
ti = Pin(0,Pin.IN)

# get the time from the MSF60 signal - this takes over 1 minute to complete
TheTime = Decode_MSF(ti,sw)
print(TheTime)

if TheTime[0] == True:
    # set the Pico's RTC based on the recieved signal's time
    rtc = machine.RTC()
    rtc.datetime(TheTime[1])

    # continuously print the time
    while True:
        print(rtc.datetime())
        utime.sleep(1)

#A = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0]
#B = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1]

#validate_MSF(A,B)