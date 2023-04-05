# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

# Complete project details at https://RandomNerdTutorials.com
# Quick reference. https://docs.micropython.org/en/v1.15/esp32/quickref.html

import machine
import time
import uos
from umqtt.robust import MQTTClient
import ubinascii
import micropython

## init sensors and actuators
# set sensors
from sensors import init_all_sensors
sensor_list = init_all_sensors()

# set actuators
from actuators import init_all_actuators
actuator_list = init_all_actuators()


def no_debug():
    # Debugging messages
    import esp
    # None - turn off vendor O/S debugging messages
    # 0 - redirect vendor O/S debugging messages to UART(0)
    esp.osdebug(None)


# Garbage collector
import gc
gc.collect()  # activate garbage collector

# WLAN
ssid = "PiEmbedded"
password = "bruemmer"

# MQTT
mqtt_broker = "192.168.4.1"
client_id = b'52dc166c-2de7-43c1-88ff-f80211c7a8f6'
# subscribed topics
# Quality of Service (QoS) - defines the guarantee of delivery for a specific message
# https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/
subscription_topic = b"garden/lab/"


# connect to WLAN
def do_connect():
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Connection successful")

    ## if success, install mqtt packages


#     import upip
#     upip.install('micropython-umqtt.simple')
#     upip.install('micropython-umqtt.robust')


## print information about connection
## IP address, subnet mask, gateway and DNS server
# print('network config:', wlan.ifconfig())

no_debug()
do_connect()
