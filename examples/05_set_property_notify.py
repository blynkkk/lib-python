"""
[SET_PROPERTY/NOTIFY EXAMPLE] ==========================================================================================

Environment prepare:
In your Blynk App project:
  - add "Slider" widget,
  - bind it to Virtual Pin V5,
  - set values range 0-255
  - add "LED" widget and assign Virtual Pin V5 to it
  - add "Notification" widget to be allowed receive notifications in App
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example and run it


This started program will periodically call and execute event handler "write_virtual_pin_handler".
In app you can move slider that will cause LED brightness change and will send virtual write event
to current running example. Handler will set random color for virtual pin and will send notification
event to App. Virtual pin property 'color' change will cause color changes for "Slider" and "LED" widgets
In App user will get notifications about color change event.

Schema:
=====================================================================================================================
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
     |          |       pin set property              |    pin property changed msg        |
     +-----+--->------------------------------------->------------------------------------>+
           |    |                                     |                                    |
           |    |          send notification          |     notification widget present?   |
           +--->------------------------------------->------------------------------------>+
                |                                     |                                    |
                |                                     |              yes                   |
                |                                     +<-----------------------------------+
                |                                     |                                    |
                |                                     |                                    |
                |                                     +----------------------------------->+
                +                                     +        notification delivery       +

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
import random

BLYNK_AUTH = 'YourAuthToken'
blynk = blynklib.Blynk(BLYNK_AUTH)

NOTIFY_MSG = "['COLOR' = '{}']"
colors = {'#FF00FF': 'Magenta', '#00FF00': 'Lime'}


@blynk.handle_event('write V5')
def write_handler(pin, value):
    current_color = random.choice(colors.keys())
    blynk.set_property(pin, 'color', random.choice(colors.keys()))
    blynk.notify(NOTIFY_MSG.format(colors[current_color]))
    print(NOTIFY_MSG.format(colors[current_color]))


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
