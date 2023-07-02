import utime
from machine import Pin

from DST import DST_offset

# Encodes a date and time in MSF60 list - for debugging or sync'ing

# Define Constants for the decoding

YR = [80,40,20,10,8,4,2,1] # Year
MT = [10,8,4,2,1] # Month
DY = [20,10,8,4,2,1] # Day
WK = [4,2,1] # Day of Week; 0 = Sunday; 6 = Saturday
HR = [20,10,8,4,2,1] # Hour
MN = [40,20,10,8,4,2,1] # Minute

MINUTE_TERMINATOR = [0,1,1,1,1,1,1,0]

WHOLE_DATETIME = [YR,MT,DY,WK,HR,MN]


def BCD(weight,dec):
    # undertake BCD conversion with the varying length weights to proide the equivalent binary list that MSF outputs
    
    # create the output with same size as the weighting list
    bcd = [0] * len(weight)
    
    quot = dec
    
    for i in range(0,len(weight)):
       
        rem = quot % weight[i]
        
        # if the remainder is less than the quotient then a whole division has occured and therefore output a 1; otherwise output a zero
        bcd[i] = int(rem < quot)
        
        # if a whole division has occured, the remainder becomes the next to try on the next iteration throught the weights 
        if rem < quot:
            quot = rem
        
        #print("WEIGHT:",weight[i])
        #print("REM:",rem)
        #print("QUOT:",quot)
        
    return(bcd)


def MSF_ENCODE(date_time):
    #print(len(date_time))
    #print(len(WHOLE_DATETIME))
    
    # lengths must be equivalent otherwise things will go wrong
    if len(date_time) != len(WHOLE_DATETIME):
        raise Exception(f"Tuple to encode must have {len(WHOLE_DATETIME)} items, but received {len(date_time)}")

    # create list with the first item as the first empty 16 bits from the MSF signal
    A_temp = [[0]*16]

    # add each of the relevant BCD encoded sections to A_temp so that we will have 7 individual lists of the BCD items
    for i in range(0,len(WHOLE_DATETIME)):
        A_temp.append(BCD(WHOLE_DATETIME[i],date_time[i]))
        
    # Add in minute terminator
    A_temp.append(MINUTE_TERMINATOR)
    
    # A_temp now contains all 59 bits to define a time and date, but they are in 8nr "boxes"
    
    #print(A_temp)
    
    # create A by unpacking all the bits into one list
    A = []
    
    for i in A_temp:
        for bit in i:
            A.append(bit)
            
    #print(A)
    
    # create equivalent bit B - assuming DUT is all zero and no warning of BST
    B = [0] *59
    
    B[53] = int(not(sum(A[16:24]) % 2))
    #print(A[16:24])
    B[54] = int(not(sum(A[24:35]) % 2))
    #print(A[24:35])
    B[55] = int(not(sum(A[35:38]) % 2))
    B[56] = int(not(sum(A[38:51]) % 2))
    
   
    # set BST bit if necessary
    B[57] = DST_offset((date_time[0]+2000,date_time[1],date_time[2],date_time[3],date_time[4],date_time[5],0,0))
    #print(B[57])
    
    #print(B)
    
    return(A,B)


def MSF_TRANSMIT(date_time,pin):
    # transmit the MSF signal over gpio pin
    # transmit signal as 1 = off; 0 = on as this is how the generic MSF60 module decodes it
    
    ti = Pin(pin,Pin.OUT, pull=Pin.PULL_UP)
    
    # signal takes exactly 1 minute to transmit, and pulses are at 0.1s intervals

    # generate whole signal prior to transmission
    # 1 minute = 600 bits at 0.1s intervals
    
    S = [0]*599
    #print(S)
    
    # get bit's A and B
    A,B = MSF_ENCODE(date_time)
    
    # first 500ms is off(1); followed by 500ms of on(0)
    S[0:4] = [1] * 5
    
    
    for i in range(1,60):
        # start of each second is off(1)
        S[(10 * i)] = 1
    
        # each 1st 100ms after each second is bit A
        S[(10 * i + 1)] = A[i-1]
        
        # each 2nd 100ms after each second is bit B
        S[(10 * i + 2)] = B[i-1]
    
    #print(S[0:300])
    #print(S[300:600])
        
    # transmit over pin as a series of on/off at 0.1s pulses
    
    # get starting time so pulses can be sent
    t1 = utime.ticks_ms()
    #t2=t1 # debug for measuring how long code takes to run
    
    # iterate through all items in the carrier signal
    for i in S:
        # issue each pulse once 100ms has elapsed (0.1s)
        while utime.ticks_diff(utime.ticks_ms(),t1) < 100:
            #print(i)
            ti.value(i) # set value on the pin to the signal
            #utime.sleep(0.05) # prevent hammering of the processor
        print(i)
        t1 = utime.ticks_ms()

    #print(utime.ticks_diff(t1,t2)) # how long code has taken to run - should be 60s




# Format (last two digits of year, month, day, weekday, hour, minute)
#ToEncode = (23,7,1,6,10,48)

#MSF_TRANSMIT(ToEncode,16)