import network
import espnow
from machine import Pin
import time

recieveresp = b'\xE0\x8C\xFE\x32\xB5\x48' #put the reciever esp have to ask arshia 

wifi = network.WLAN(network.STA_IF)
wifi.active(True) #testing cuz Im not sure if we have to add the thing per say

e = espnow.ESPNow()
e.active(True)
e.add_peer(recieveresp)

#brrrrrrrr buttons 
up = Pin(13, Pin.IN, Pin.PULL_UP)
down = Pin(12, Pin.IN, Pin.PULL_UP)
left = Pin(14, Pin.IN, Pin.PULL_UP)
right = Pin(27, Pin.IN, Pin.PULL_UP)
jump = Pin(26, Pin.IN, Pin.PULL_UP)
start = Pin(25, Pin.IN, Pin.PULL_UP)
stop = Pin(33, Pin.IN, Pin.PULL_UP) #I might change the toggle input here 
#brrrrrrrr buttons

while True:
    data = "{},{},{},{},{},{},{}".format( #putting the string values which is console buttons can be changed later
        up.value(),
        down.value(),
        left.value(),
        right.value(),
        jump.value(),
        start.value(),
        stop.value()
    )

    e.send(recieveresp, data)
    time.sleep(0.05)