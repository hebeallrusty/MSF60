from machine import Pin
from MSF import *
import utime
import _thread

# turn on the MSF60 module - this one has a P pin which requires logic low to start the pulses on pin T. sw is connected to pin P.
sw = Pin(1,Pin.OUT, Pin.PULL_DOWN)

# ti is connected to pin T. This is where the pulses are read from.
ti = Pin(0,Pin.IN, Pin.PULL_DOWN)

def get_time():
    global rtc
    global TheTime
    # get the time from the MSF60 signal - this takes over 1 minute to complete
    while TheTime[0] == False:
        TheTime = Decode_MSF(ti,sw)
    print(TheTime)
    print("setting time...")
    # set the Pico's RTC based on the recieved signal's time

    rtc.datetime(TheTime[1])    


def print_time():
    global rtc
    while True:
        print(rtc.datetime())
        utime.sleep(1)
            
TheTime = [False,(2000,1,1,0,0,0,0,0)]
rtc = machine.RTC()
rtc.datetime(TheTime[1])

second_thread = _thread.start_new_thread(get_time, ())

print_time()

#A = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0]
#B = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1]

#validate_MSF(A,B)