"""
Blynk is a platform with iOS and Android apps to control
Arduino, Raspberry Pi and the likes over the Internet.
You can easily build graphic interfaces for all your
projects by simply dragging and dropping widgets.
  Downloads, docs, tutorials: http://www.blynk.cc
  Sketch generator:           http://examples.blynk.cc
  Blynk community:            http://community.blynk.cc
  Social networks:            http://www.fb.com/blynkapp
                              http://twitter.com/blynk_app

This example shows how to display custom data on the widget.
In your Blynk App project:
  - add "Value Display" widget,
  - bind it to Virtual Pin V11,
  - set values range 0-255
  - set the read frequency to 5 second.
  - optionally(to have more visibility) you can add "LED" widget and assign Virtual Pin V11 to it
  - Run the App (green triangle in the upper right corner).


This started program will periodically call and execute event handler "read_virtual_pin_handler".
Calling virtual_write operation inside handler updates widget value.
In app you can see updated values and optionally LED brightness change.
"""

import BlynkLib
import random

BLYNK_AUTH = 'YourAuthToken'

# initialize blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

READ_PRINT_MSG = """[READ_VIRTUAL_PIN_EVENT] Pin: V{}"""


# register handler for virtual pin V11 reading
@blynk.handle_event("read V11")
def read_virtual_pin_handler(pin):
    print(READ_PRINT_MSG.format(pin))
    blynk.virtual_write(pin, random.randint(0, 255))


# infinite loop that waits for event
while True:
    blynk.run()
