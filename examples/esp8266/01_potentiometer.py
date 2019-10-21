# -*- coding: utf-8 -*-
"""
[Slide Potentiometer NodeMcu ESP8266] ===============================================================================

ESP8266 pinout:
    https://i.imgur.com/HgVTxCh.png

Slide Potentiometer:
    - connect VCC sensor line to "+3.3v" board pin
    - connect GND sensor line to "ground" board pin
    - connect DATA sensor line to board A0 pib (ADC - analog to digital conversion on dedicated pin)

Environment prepare:
In your Blynk App project:
    - add "Gauge" widget,
    - bind it to Virtual Pin V1
    - set name "Potentiometer"
    - set label /pin.##/
    - set update time=1 sec and assign 0-1024 values range to it


    - Run the App (green triangle in the upper right corner).
    - define SSID and WiFi password that will be used by ESP32 board
    - define your auth token for current example and run it

This started program will periodically call and execute event handler "read_virtual_pin_handler".
that will try to get data from potentiometer and write it to related virtual pin.
Within App widget gauge value will be updated each 1 sec.
=====================================================================================================================
Additional info about blynk you can find by examining such resources:

    Downloads, docs, tutorials:     http://www.blynk.cc
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================================
"""
import blynklib_mp as blynklib
import network
import utime as time
import machine

WIFI_SSID = 'YourWifiSSID'
WIFI_PASS = 'YourWifiPassword'
BLYNK_AUTH = 'YourAuthToken'

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
adc = machine.ADC(0)


@blynk.handle_event('read V1')
def read_handler(vpin):
    p_value = adc.read()
    print('Current potentiometer value={}'.format(p_value))
    blynk.virtual_write(vpin, p_value)


while True:
    blynk.run()
