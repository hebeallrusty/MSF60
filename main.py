from machine import Pin
import utime

# MSF60 module works with the inverted signal i.e. 0 = on; 1 = off. This is useful for making the binary code decimal (bcd) easier to work with

# Each second of MSF60 is represented by [0,0,0,0,0,1] if samples are taken at 0.1s (the 1 marking the start of the second).
# The minute mark is represented by [1,1,1,1,1,0,0,0,0,0] if samples are taken at each 0.1s
# Bit A is the first 0.1s pulse after the second mark (and is not used i.e. set to 0 for the first 16 second
# Bit B is the second 0.1s pulse after the second mark.
# each second is preceeded by at least 0.5s of signal (i.e. 0)

# 

# turn on the MSF60 module - this one has a P pin which requires logic low to start the pulses on pin T. sw is connected to pin P.
sw = Pin(1,Pin.OUT, Pin.PULL_DOWN)

# ti is connected to pin T. This is where the pulses are read from.
ti = Pin(0,Pin.IN)

# each section of the signal has a separate method of binary representation; define each of the binary digits
YR = [80,40,20,10,8,4,2,1] # Year
MT = [10,8,4,2,1] # Month
DY = [20,10,8,4,2,1] # Day
WK = [4,2,1] # Day of Week; 0 = Sunday; 6 = Saturday
HR = [20,10,8,4,2,1] # Hour
MN = [40,20,10,8,4,2,1] # Minute

# separate representation of the day of the week in the same order as the signal representation
DOY = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

# representation of the minute marker
SYNC = [1,1,1,1,1,0,0,0,0,0]

# representation of the second mark
SEC = [0,0,0,0,0,1]

# set up variables for each calculation of the BCD with the signal received
yr = 0
mt = 0
dy = 0
wk = 0
hr = 0
mn = 0


# set a loop to run forever
while True:
    
    # counters to keep track of where we are
    
    n = 0
    m = 0 # for elapsed seconds
    s = 0 # for sync
    
    # for Bit A and Bit B of the signal
    A = []
    B = []
    
    # buffer for keeping track of what we are comparing against and allowing us to search the signal
    unit = []
    # remember signal is inverted
    
    # 

    # keep reading the signal until we find the minute mark
    while unit != SYNC:
        
        # sleep for 0.1s i.e wait for the next sample
        utime.sleep(0.1)           
        
        # read the signal and add it to the end of the unit buffer
        unit.append(int(ti.value()))
           
        
        # we only want to look at a whole second so that we don't fill the memory until it is full
        if len(unit) <= 10:
            # if the buffer has less than 10 items (i.e less than a second), keep adding to the buffer
            pass
        else:
            # once the buffer is full of 10 items (a second's worth); get rid of the first item so that the buffer only contains the most recent signal
            
            unit = unit[1:]
        

        
        print(unit)
    
    # once broken out of the loop above, we must have found the minute marker.
    
    print("SYNCED TO MINUTE")
    
    # we have sync
    s = 1
    
    # remove all items from the buffer so that we can then start looking at seconds so that we keep in sync with the signal
    
    # capture each second now that we have the marker but make the buffer so that it only has the start of each second
    
    unit = unit[5:]
    
    # unit should then be [0,0,0,0,0] which is the end of a second
    
    # check for the first [1] of a second which will be [0,0,0,0,0,1]
    
    while len(A) <= 59:
        utime.sleep(0.1)
        unit.append(int(ti.value()))
        print(unit)
        
        while unit != SEC:
            #print(unit)
            
            # ensure we stay in sync; if m gets too big then we have definitely lost sync and therefore we can break out as we'll have lost the accuracy
            m += 1
            #print(m)
            # get the next sample
            utime.sleep(0.1)
        
            # add it too the buffer
            unit.append(int(ti.value()))
            
            
            # we only want to look at the last 6 samples for [0,0,0,0,0,1]
            if len(unit) <= 6:
                pass
            elif m > 10: # waited too long m should get to 7
                # lost sync therefore flag it up
                print("lost sync")
                s = 0
                break
            else:
                # get rid of the first item
                unit = unit[1:]
                #print(unit)
        
        # if we have lost sync; break out of loop
        
        # reset the counter for sync
        m = 0
        if s == 0:
            break
        
        utime.sleep(0.1)
        
        A.append(int(ti.value()))
        print("A is: ",A[-1])
        
        utime.sleep(0.1)
        
        B.append(int(ti.value()))
        unit = []
        
            
#     print(DOY[wk],"-",dy,"-",mt,"-",yr,"-",hr,"-",mn)
    
    yr = sum( x * y for x,y in zip(A[16:24],YR))
    
    mt = sum( x * y for x,y in zip(A[24:29],MT))
    
    dy = sum( x * y for x,y in zip(A[29:35],DY))
    
    wk = sum( x * y for x,y in zip(A[35:38],WK))
    
    hr = sum( x * y for x,y in zip(A[38:44],HR))
    
    mn = sum( x * y for x,y in zip(A[44:51],DY))
    
    print(DOY[wk],"",dy,"/",mt,"/",yr," ",hr,":",mn)
              
    
    print(A)
    print(" ")
    print(B)
    break
    
    #while ti.value():
    #    n +=1
    #    s +=1
    #print(ti.value())
    #    utime.sleep(0.1)
    #print("off:",n, " ms")
    
    #while ti.value() == False:
    #    m +=1
    #    utime.sleep(0.1)
        
    #print("on:",m, " ms")
    
