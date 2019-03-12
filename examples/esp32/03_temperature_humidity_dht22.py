# -*- coding: utf-8 -*-
"""
[TEMPERATURE/HUMIDITY SENSOR (DHT22) ESP32 TTGO T8 V1.7] ============================================================

ESP32 pins schema:
    https://images-na.ssl-images-amazon.com/images/I/81%2Bjpo9-D8L._SX522_.jpg

DHT22 sensor:
    - connect VCC sensor line to "+5" board pin
    - connect GND sensor line to "ground" board pin
    - connect DATA sensor line to board GPIO 4

    DHT22 datasheet that may be helpful:
    https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf

Environment prepare:
In your Blynk App project:
    - add "Gauge" widget,
    - bind it to Virtual Pin V3
    - set name "Temperature"
    - set label /pin.##/°C
    - set update time=15 sec and assign 0-100 values range to it

    - add "Gauge" widget,
    - bind it to Virtual Pin V4
    - set name "Humidity"
    - set label /pin.##/ %
    - set update time=15 sec and assign 0-100 values range to it


  - Run the App (green triangle in the upper right corner).
  - define SSID and WiFi password that will be used by ESP32 board
  - optionally change HW GPIO pin that will be used by touch button data line
  - define your auth token for current example and run it

This started program will periodically call and execute event handler "read_virtual_pin_handler".
that will try to get data from sensor and write them to related virtual pins.
Within App widget values will be updated each 15 sec.
If during cycle there was error in get data operation  - widget colors will be changed to grey (aka disabled state)
and restored on next successful read sensor data operation.
=====================================================================================================================
Additional info about blynk you can find by examining such resources:

    Downloads, docs, tutorials:     http://www.blynk.cc
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================================
"""
import blynklib
import network
import utime as time
from machine import Pin

# DHT driver already included into Micropython software as core module
# so we just import it
import dht

WIFI_SSID = 'YourWifiSSID'
WIFI_PASS = 'YourWifiPassword'
BLYNK_AUTH = 'YourAuthToken'
GPIO_DHT22_PIN = 4

print("Connecting to WiFi network '{}'".format(WIFI_SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)
while not wifi.isconnected():
    time.sleep(1)
    print('WiFi connect retry ...')
print('WiFi IP:', wifi.ifconfig()[0])

print("Connecting to Blynk server...")
blynk = blynklib.Blynk(BLYNK_AUTH)

T_COLOR = '#f5b041'
H_COLOR = '#85c1e9'
ERR_COLOR = '#444444'

T_VPIN = 3
H_VPIN = 4

dht22 = dht.DHT22(Pin(4, Pin.IN, Pin.PULL_UP))


@blynk.handle_event('read V{}'.format(T_VPIN))
def read_handler(vpin):
    temperature = 0.0
    humidity = 0.0

    # read sensor data
    try:
        dht22.measure()
        temperature = dht22.temperature()
        humidity = dht22.humidity()
    except OSError as o_err:
        print("Unable to get DHT22 sensor data: '{}'".format(o_err))

    # change widget values and colors according read results
    if temperature != 0.0 and humidity != 0.0:
        blynk.set_property(T_VPIN, 'color', T_COLOR)
        blynk.set_property(H_VPIN, 'color', H_COLOR)
        blynk.virtual_write(T_VPIN, temperature)
        blynk.virtual_write(H_VPIN, humidity)
    else:
        # show widgets aka 'disabled' that mean we had errors during read sensor operation
        blynk.set_property(T_VPIN, 'color', ERR_COLOR)
        blynk.set_property(H_VPIN, 'color', ERR_COLOR)


while True:
    blynk.run()
