"""
[WRITE VIRTUAL PIN EXAMPLE] ========================================================================

Environment prepare:
In your Blynk App project:
  - add "Slider" widget,
  - bind it to Virtual Pin V4,
  - set values range 0-255
  - add "LED" widget and assign Virtual Pin V4 to it
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example and run it


This started program will periodically call and execute event handler "write_virtual_pin_handler".
In app you can move slider that will cause LED brightness change and will send virtual write event
to current running example. Handler will print pin number and it's updated value.

Schema:
====================================================================================================
          +-----------+                        +--------------+                    +--------------+
          |           |                        |              |                    |              |
          | blynk lib |                        | blynk server |                    |  blynk app   |
          |           |                        |  virtual pin |                    |              |
          |           |                        |              |                    |              |
          +-----+-----+                        +------+-------+                    +-------+------+
                |                                     |                                    |
                |                                     |  write event from "Slider" widget  |
                |                                     |                                    |
                |                                     +<-----------------------------------+
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
 event handler  |   write event to hw from server     |                                    |
(user function) |                                     |                                    |
     +-----------<------------------------------------+                                    |
     |          |                                     |                                    |
     |          |                                     |                                    |
     +--------->+                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                +                                     +                                    +
====================================================================================================
Additional blynk info you can find by examining such resources:

    Downloads, docs, tutorials:     http://www.blynk.cc
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
====================================================================================================
"""

import blynklib

BLYNK_AUTH = 'YourAuthToken'

# initialize Blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

WRITE_EVENT_PRINT_MSG = """[WRITE_VIRTUAL_PIN_EVENT] Pin: V{} Value: '{}'"""


# register handler for virtual pin V11 write event
@blynk.handle_event("write V4")
def write_virtual_pin_handler(pin, value):
    print(WRITE_EVENT_PRINT_MSG.format(pin, value))


# infinite loop that waits for event
while True:
    blynk.run()
