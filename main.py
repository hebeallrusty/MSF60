from machine import Pin
import utime

sw = Pin(1,Pin.OUT, Pin.PULL_DOWN)

ti = Pin(0,Pin.IN)

YR = [80,40,20,10,8,4,2,1]
MT = [10,8,4,2,1]
DY = [20,10,8,4,2,1]
WK = [4,2,1] # 0 = Sunday; 6 = Saturday
HR = [20,10,8,4,2,1]
MN = [40,20,10,8,4,2,1]

DOY = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

yr = 0
mt = 0
dy = 0
wk = 0
hr = 0
mn = 0

while True:
    
    n = 0
    m = 0
    s = 0
    A = []
    B = []
    
    unit = []
    # signal is inverted - True indicates a Zero; False is a one
    
    
    sync = [0,0,0,0,0,1,1,1,1,1]
    
    while unit != sync:
        unit.append(int(ti.value()))
        if len(unit) <= 10:
            pass
        else:
            unit.pop(0)
        
        utime.sleep(0.1)
        print(unit)
        
    print("SYNCED TO MINUTE")
    
    # capture each second now that we have the marker
    
    unit = []
    
    while len(A) <= 59:
        unit.append(int(ti.value()))
        n +=1
        
        if n == 10:
            print(unit)
            A.append(unit[6])
            B.append(unit[7])
            n = 0
            unit =[]
            
        utime.sleep(0.1)
    print("times up")
    print(A)
    print(B)
    
    # Year calc
    for i in range(0,len(YR)):
        yr = yr + (A[i + 16] * YR[i])
        #print(year)
        
    for i in range(0,len(MT)):
        mt = mt + (A[i + 24] * MT[i])
        
    for i in range(0,len(DY)):
        dy = dy + (A[i + 29] * DY[i])
        
    for i in range(0,len(WK)):
        wk = wk + (A[i + 35] * WK[i])
        
    for i in range(0,len(HR)):
        hr = hr + (A[i + 38] * HR[i])
        
    for i in range(0,len(MN)):
        mn = mn + (A[i + 38] * MN[i])
        
    print(DOY[wk],"-",dy,"-",mt,"-",yr,"-",hr,"-",mn)
        
    
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
    
