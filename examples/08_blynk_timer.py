"""
[BLYNK TIMER EXAMPLE] ============================================================================================

Environment prepare:
In your Blynk App project:
  - add "SuperChart" widget
  - add two data streams for it ( stream #1 - Virtual Pin 8, stream #2 - Virtual Pin 9)
  - set different colors for data stream (ex. red and orange)
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example and run it


This started program will register two timers that will update Virtual Pins data after defined intervals.
In app you can see on graph both pins data change. Additionally timers will print new pin values info to stdout.

Schema:
=================================================================================================================
       +-----------+                        +--------------+                    +--------------+
       |           |                        |              |                    |              |
       | blynk lib |                        | blynk server |                    |  blynk app   |
       |           |                        |  virtual pin |                    |              |
       |           |                        |              |                    |              |
       +-----+-----+                        +------+-------+                    +-------+------+
             |                                     |                                    |
             |                                     |                                    |
             |                                     |                                    |
             |                                     |                                    |
+------------+                                     |                                    |
|  +---------+                                     |                                    |
|  |         |  update virtual pin 8 value         |                                    |
|  |         |                                     |    notify app about vpin 8 update  |
|  +-------->------------------------------------->+                                    |
|            |                                     +----------------------------------->+
+----------->------------------------------------->+                                    |
             |                                     +----------------------------------->+
             |  update virtual pin 9 value         |                                    |
             |                                     |    notify app about vpin 9 update  |
             |                                     |                                    |
             |                                     |                                    |
             |                                     |                                    |
             +                                     +                                    +

================================================================================================================
Additional blynk info you can find by examining such resources:

    Downloads, docs, tutorials:     https://blynk.io
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
====================================================================================================
"""

import blynklib
import blynktimer
import random

BLYNK_AUTH = 'YourAuthToken'  # insert your Auth Token here
blynk = blynklib.Blynk(BLYNK_AUTH)

# create timers dispatcher instance
timer = blynktimer.Timer()

WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_WRITE] Pin: V{} Value: '{}'"


# Code below: register two timers for different pins with different intervals
# run_once flag allows to run timers once or periodically
@timer.register(vpin_num=8, interval=4, run_once=False)
@timer.register(vpin_num=9, interval=7, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = random.randint(0, 20)
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)


while True:
    blynk.run()
    timer.run()
