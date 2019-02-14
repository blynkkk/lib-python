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
  Add a Value Display widget,
  bind it to Virtual Pin V2,
  set the read frequency to 1 second.
  Run the App (green triangle in the upper right corner).
It will automagically call v2_read_handler.
Calling virtual_write updates widget value.
"""

import BlynkLib

BLYNK_AUTH = 'YourAuthToken'

# initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)


# register handler for virtual pins
@blynk.handle_event("write V11")
def write_vpin_handler(pin, value):
    print("{}\n[USER_WRITE_HANDLER] Pin: V{} Value: {}\n{}".format("=" * 50, pin, value, "=" * 50))


while True:
    blynk.run()
