from machine import Pin #, ADC
from MSF import validate_MSF
import utime

# requires an inverted signal i.e. 1 is off; 0 is on

# generic sensor outputs 1 when it is off - therefore work with inverted signal!

# representation of the minute marker
MINUTE_MARKER = [1,1,1,1,1,0,0,0,0,0]
SECOND_MARKER = [0,0,0,0,1]

#t3 = utime.ticks_ms()



def MSF_RECEIVE(ti):
    print("Running")
    
    Received_Time = [False]
    
    # Logic of capturing the signal
    # try and filter out minor interferance -
    # - take as many samples at 10ms intervals,
    # - average value the signal over this 10ms
    # - if the average is close to a one or zero, then keep the sample as valid.
    # -  - discard the sample if it is too "fuzzy"
    # - take the average (of the valid) 10 x 10ms samples which should get what each 100ms pulse value is

    v = 0 # for taking the average of the sub-10ms samples (sub-samples)
    n = 0 # keep track of how many sub-samples have been taken each 10ms

    m = 0 # to keep track of how many 10ms intervals have been taken - 10 x 10ms = 1 pulse of the MSF signal

    q = 0 # for averaging out what each 10ms interval was - a one or a zero
    #valid_sample = 0 # whether the 10ms sample was valid or not (i.e was very close to a one or a zero)
    
    t1 = utime.ticks_ms() # to allow the sub-samples to be taken each 10ms
    unit = [] # buffer for the output

    # empty lists for Bit A and Bit B of the signal
    A = []
    B = []

    # for keeping track of how many times the second marker has missed when collecting bit A and bit B
    # if it gets too large, we have become de-sync'd from the signal
    r = 0 

    sync = False # flag for when the minute marker has been found

    while Received_Time[0] == False:
        
        
        
        # take as many samples within (approx) 10ms
        while utime.ticks_diff(utime.ticks_ms(),t1) < 10:
            
            # get the raw sensor value
            vx = ti.value()
            
            # add each sub-sample so it can be averaged once the 10ms sampling period has expired
            v += vx
            
            #print(vx)
            
            # keep track of how many samples have been taken (for averaging)
            n += 1 # how many samples we have taken
            
            #utime.sleep(0.001) # to stop hammering the processor - approx 10 samples at 10ms intervals with rp2040
        #print("n:",n)


        #print(v/n)
        
        # average each 10ms sub-sample and set it's sample as either a 1 or zero
        if (v/n) < 0.5: # the average of the sub-samples in that 10ms interval was "low"
            
            # add the sample's value for averaging
            q += 1 # signal is inverted, so if it's a zero, its actually a one. 

        else:
            q = q # signal is inverted, so if it's "high" its actually a zero

        # reset n for the sub-sampling
        n = 0
        
        # count how many 10ms interval samples we have
        m += 1 # 
        
        #print(q/m)
        
        #print(m)
        
        # if we have 10 x 10ms samples - we must now have 100ms of the signal i.e. 1nr pulse
        if m == 10: # q now has 10nr average samples of 10ms each, i.e. 100ms (0.1s)
            m = 0 # reset m so that we can keep checking how many 10ms samples we have

            #print(q)
            
            # take the average of this 100ms sample
            q = q / 10
            
            #print(q)
            
            # set this 100ms sample to either a one or zero
            
            if q < 0.5: # if it's above a half, then its a 1; make signal inverted
                s = 1
            else:
                s = 0
            
            # DEBUG - show the Signal received
            #print(s)
            
            # reset q so that the next average can be taken
            q = 0
            
            t3 = utime.ticks_ms()
            
            # add the sample to the buffer
            unit.append(s)
            
            # search for the minute marker once we have a whole second in the buffer
            if len(unit) <= 9:
                pass # keep adding to the buffer until we have a whole second
                
            else: # 10 samples held in unit i.e. a whole second
                
                # DEBUG - show the last second
                #print(unit)
                
                if unit == MINUTE_MARKER:
                    
                    print("MINUTE MARKER") # end of the zero second i.e. the next sample is the start of 01 secs past the minute
                    
                    # make a note of the time that the minute marker ended so that when time has been decoded, we can correct for processing and verification time past the last sample
                    tx = utime.time() 
                    
                    # flag that we now have sync
                    sync = True
                    
                # move the buffer on one more by removing the first bit.
                unit = unit[1:]
                
            if sync == True:
                
                # DEBUG - show current buffer
                #print(unit)
                
                # buffer contains a rolling 1 second, so 2 x 100ms after the minute will be both bit A and bit B
                if unit[2:7] == SECOND_MARKER:
                    r = 0 # reset r so that we keep track of being in sync
                    
                    # the last two items of the buffer have both bit A and bit B, so add them to the relevant lists.
                    A.append(unit[7])
                    B.append(unit[8])
                    print("A:",unit[7])
                    
                else: # unit buffer miss, but this is normal as it's a rolling buffer, but if we miss too many times, we have definitely lost sync
                    r += 1 # record how many times we have missed
                    
                    #print(r)
                    
                    if r > 9: # should be no more than 9 between seconds
                        # sync lost therefore reset everything
                        print("Lost sync!")
                        r = 0
                        A = []
                        B = []
                        sync = False
                
                if len(A) == 59: # we have a full complement of bits for the time signal and can now decode it
                    # debug
                    print(A)
                    
                    Received_Time = validate_MSF(A,B)
                    
                    if Received_Time[0] == True:
                        # time is likely to be correct, so return with the time
                        return(Received_Time)
                    else:
                        # time is incorrect, so keep trying
                        print("Validation Failed")
                        print(Received_Time)
                        r = 0
                        A = []
                        B = []
                        sync = False
                    #print(Received_Time)
                    #print(A)
                    
                #print(unit[2:7])
        #print(utime.ticks_diff(utime.ticks_ms(),t3))
        # reset the time so that the above loop keeps triggering each 10ms
        t1 = utime.ticks_ms()
        v = 0
        #q = 0
        #m = 0
        #n = 0


# turn on the MSF60 module - this one has a P pin which requires logic low to start the pulses on pin T. sw is connected to pin P.
sw = Pin(1,Pin.OUT, Pin.PULL_DOWN)
#sw.off()

# ti is connected to pin T. This is where the pulses are read from.
ti = Pin(0,Pin.IN, Pin.PULL_DOWN)

MSF_RECEIVE(ti)
print("DONE!")  
