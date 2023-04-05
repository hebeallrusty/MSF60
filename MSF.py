
import utime

# MSF60 module works with the inverted signal i.e. 0 = on; 1 = off. This is useful for making the binary code decimal (bcd) easier to work with

# Each second of MSF60 is represented by [0,0,0,0,0,1] if samples are taken at 0.1s (the 1 marking the start of the second).
# The minute mark is represented by [1,1,1,1,1,0,0,0,0,0] if samples are taken at each 0.1s
# Bit A is the first 0.1s pulse after the second mark (and is not used i.e. set to 0 for the first 16 second
# Bit B is the second 0.1s pulse after the second mark.
# each second is preceeded by at least 0.5s of signal (i.e. 0)

# referenced from https://www.npl.co.uk/msf-signal

# each section of the signal has a separate method of binary representation; define each of the binary digits
YR = [80,40,20,10,8,4,2,1] # Year
MT = [10,8,4,2,1] # Month
DY = [20,10,8,4,2,1] # Day
WK = [4,2,1] # Day of Week; 0 = Sunday; 6 = Saturday
HR = [20,10,8,4,2,1] # Hour
MN = [40,20,10,8,4,2,1] # Minute

# separate representation of the day of the week in the same order as the signal representation
DOY = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

DAYS_IN_MONTH = [31,28,31,30,31,30,31,31,30,31,30,31]


def Decode_MSF(ti,sw):
    # ti is the pulse of the MSF60 signal
    # sw is the switch to turn on the signal

    # representation of the minute marker
    SYNC = [1,1,1,1,1,0,0,0,0,0]

    # representation of the second mark
    SEC = [0,0,0,0,0,1]

    
    # counters to keep track of where we are
    m = 0 # for elapsed samples in each sync period of the second

    
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
    #s = 1
    
    # remove all items from the buffer so that we can then start looking at seconds so that we keep in sync with the signal
    
    # capture each second now that we have the marker but make the buffer so that it only has the start of each second
    
    unit = unit[5:]
    
    #marker_time_1 = utime.ticks_ms()
    
    # unit should then be [0,0,0,0,0] which is the end of a second
    
    # check for the first [1] of a second which will be [0,0,0,0,0,1]
    
    while len(A) <= 59:
        # add the next sample to what we have. Once we have 60 bits in Bit A; then we have the whole minute
        
        utime.sleep(0.1)
        unit.append(int(ti.value()))
        
        #print(unit)
        
        # sync up to the second
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
                # lost sync therefore fail and return
                
                print("lost sync")
                #s = 0
                return([False,"Lost Sync with signal"])
            else:
                # get rid of the first item
                unit = unit[1:]
                #print(unit)
        
       
        # reset the counter for sync
        m = 0

        # get the next sample and add it to Bit A's list
        utime.sleep(0.1)
        
        A.append(int(ti.value()))
        print("A is: ",A[-1])
        
        # get the next sample and add it to Bit B's list
        utime.sleep(0.1)
        
        B.append(int(ti.value()))
        
        # reset the buffer to start again
        unit = []


    # after breaking out the loop we are at 60th second, so record wall time so that we can then return the seconds after the rest of the calculations
    # this is so that we aren't skewed by how long the calcs take as we have now hit another minute marker
    
    #marker_time_1 = utime.ticks_ms()
    
    
    #print(A)
    #print(" ")
    #print(B)
    
    # results need to be validated to see if they are reliable, offload all the calcs to the validation function for efficiency
    Received_Time = validate_MSF(A,B)
    
    if Received_Time[0] == True:
        # add in the time it's taken to validate
        #Final_Time = Received_Time[1].append(utime.ticks_diff(utime.ticks_ms(),marker_time_1)/1000)
        #print(utime.ticks_diff(utime.ticks_ms(),marker_time_1)/1000)
        return([Received_Time[0],Received_Time[1],Received_Time[2]])
    else:
        return([Received_Time[0],Received_Time[1]])
    


def validate_MSF(A,B):
    # validate if the received time is likely to be correct;
    
    # A is a list of Bit A's received from the MSF60 signal
    # B is a list of Bit B's received from the MSF60 signal
    
    # rules:
    # r1: 54B and 17A - 24A have an odd number of bits set to 1
    # r2: 55B and 25A - 35A ditto
    # r3: 56B and 36A - 38A ditto
    # r4: 57B and 39A - 51A ditto
    # r5: months are less than or equal to 12
    # r6: the day is not greater that the maximum number of days in that month
    # r7: days of the week is valid i.e saturday is day 6; day 7 is not valid - could check the day of the week is correct for the date?
    # r8: the hour is less than 24; i.e. 23:59 is the maximum time of the day
    # r9: the minute is less than 60
    
    VALIDATION_FAILED = "Signal did not pass validation"
    
    # use the property that modulo division by 2 will leave a 1 which in this case is a pass for the above rule
    
    # sum up all the bits and modulo division by 2
    r1 = (B[53] + sum(A[16:24])) % 2
    r2 = (B[54] + sum(A[24:35])) % 2
    r3 = (B[55] + sum(A[35:38])) % 2
    r4 = (B[56] + sum(A[38:51])) % 2
    
    if bool(r1 & r2 & r3 & r4) == False:
        return(False,VALIDATION_FAILED)
    
    #print(r1,r2,r3,r4)
    
    # calculate the date and time function which is just the recieved Bit A's slice multiplied by the BCD defs above and added
    yr = sum( x * y for x,y in zip(A[16:24],YR)) + 2000 # post 2000 dates only
    
    mt = sum( x * y for x,y in zip(A[24:29],MT))
    
    dy = sum( x * y for x,y in zip(A[29:35],DY))
    
    wk = sum( x * y for x,y in zip(A[35:38],WK))
    
    hr = sum( x * y for x,y in zip(A[38:44],HR))
    
    mn = sum( x * y for x,y in zip(A[44:51],MN))
    
    print([yr,mt,dy,wk,hr,mn,DOY[wk],B[57]])
    
    # date and time needs to be validated against correct values i.e the month is less than or equal to 12; the days of the month stack up etc
    # only 12 months
    r5 = (mt <= 12)
    #print("r5:",r5)
    
    if r5 == False:

        return(False,VALIDATION_FAILED)
    
    
    # month has correct number of days
    if mt == 2:
        # check leap year or not and add the result to 28. If leap-year, result of the logic statement will be 1; therefore will check if there are 29 days in Feb
        r6 = (dy <= 28 + ( yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0)))
               
    else: # rest of the months is a straight check on the correct number of days
        r6 = (dy <= DAYS_IN_MONTH[mt + 1])
    
    #print("r6:",r6)
    
    # check day of week is 6 or less - 0 is Sunday; 6 is Saturday
    r7 = (wk <= 6)
    #print("r7:",r7)
    
    # check hours are correct and less than 24
    r8 = (hr < 24)
    #print("r8:",r8)    
    
    # check minutes are less than 60
    r9 = (mn < 60)
    #print("r9:",r9)    
    
    if bool(r6 & r7 & r8 & r9) == False:
        return(False,VALIDATION_FAILED)
    
    
    # if we get here, then the signal must have passed all the tests and likely be valid
    # B[57] denotes if times is GMT (0) or BST (1); return a tuple that can be used for setting the time; Give separate extended tuple with GMT / BST and the named day of the week
    return([True,(yr,mt,dy,wk,hr,mn,0,0),(B[57],DOY[wk])])
