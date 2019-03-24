"""
[TOUCH BUTTON (TTP223B sensors) ESP32 TTGO T8 V1.7] =================================================================

ESP32 pins schema:
    https://images-na.ssl-images-amazon.com/images/I/81%2Bjpo9-D8L._SX522_.jpg

TTP223B sensor:
    - connect VCC sensor line to "+3.3v" board pin
    - connect GND sensor line to "ground" board pin
    - connect DATA sensor line to board GPIO2

Environment prepare:
In your Blynk App project:
  - add "Value Display" widget,
  - bind it to Virtual Pin V10,
  - set the read frequency to 5 second.
  - Run the App (green triangle in the upper right corner).
  - define SSID and WiFi password that will be used by ESP32 board
  - optionally change HW GPIO pin that will be used by touch button data line
  - define your auth token for current example and run it

This started program will create system IRQ with callback for "button touched" event.
Callback will store touch attempt number and touch time.
Current program will periodically call and execute event handler "read_virtual_pin_handler".
Handler reads stored last touch num and touch time values and by calling virtual_write
operation updates widget value. In app you can see touch event updated info. Ex "#10 touch at 604705274".
=====================================================================================================================
Additional info about blynk you can find by examining such resources:

    Downloads, docs, tutorials:     https://blynk.io
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


class Touch:
    num = 0
    time = 0


def callback(pin):
    print('Touch event on {}'.format(pin))
    Touch.num += 1
    Touch.time = time.time()


WIFI_SSID = 'YourWifiSSID'
WIFI_PASS = 'YourWifiPassword'
BLYNK_AUTH = 'YourAuthToken'
GPIO_PIN = 2

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

hw_pin = Pin(GPIO_PIN, Pin.IN)
hw_pin.irq(trigger=Pin.IRQ_RISING, handler=callback)


@blynk.handle_event('read V10')
def read_virtual_pin_handler(vpin):
    print('Read event on vpin {}'.format(vpin))
    blynk.virtual_write(vpin, "#{} touch at {} ".format(Touch.num, Touch.time))


while True:
    blynk.run()
