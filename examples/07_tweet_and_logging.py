"""
[TWEET AND LOGGING EXAMPLE] =========================================================================================

Environment prepare:
In your Blynk App project:
  - add "Slider" widget,
  - bind it to Virtual Pin V4,
  - set values range 0-255
  - add "Twitter Settings" widget
  - connect via this widget to your twitter account.
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example and run it


This started program will periodically call and execute event handler "write_virtual_pin_handler".
In App you can move slider that send virtual write event to current running example.
Handler will log to console this event and additionally will send tweet message with pin number and it's updated value.

Schema:
=====================================================================================================================
          +-----------+                        +--------------+                    +--------------+    +---------+
          |           |                        |              |                    |              |    |         |
          | blynk lib |                        | blynk server |                    |  blynk app   |    | twitter |
          |           |                        |  virtual pin |                    |              |    |         |
          |           |                        |              |                    |              |    |         |
          +-----+-----+                        +------+-------+                    +-------+------+    +----+----+
                |                                     |                                    |  tweet widget  |
                |                                     |                                    |      auth      |
                |                                     |                                    +--------------->+
                |                                     |                                    |      ok        |
                |                                     |  write event from "Slider" widget  +<---------------+
                |                                     |                                    |                |
                |                                     +<-----------------------------------+                |
                |                                     |                                    |                |
 event handler  |   write event to hw from server     |                                    |                |
(user function) |                                     |                                    |                |
     +-----------<------------------------------------+                                    |                |
     |          |                                     |                                    |                |
     |          |         msg for tweet widget        |                                    |                |
     +--------->-------------------------------------------------------------------------->+                |
                |                                     |                                    | real tweet msg |
                |                                     |                                    +--------------->+
                |                                     |                                    |                |
                +                                     +                                    +                +

=====================================================================================================================
Additional blynk info you can find by examining such resources:

    Downloads, docs, tutorials:     http://www.blynk.cc
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================================
"""
# uncomment line below if simple printing will be used instead of logging
# from __future__ import print_function
import blynklib
import logging

# tune console logging
_log = logging.getLogger('BlynkLog')
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
_log.addHandler(consoleHandler)
_log.setLevel(logging.DEBUG)

# uncomment line below if simple printing will be used instead of logging
# _log.info = print

BLYNK_AUTH = 'YourAuthToken'
blynk = blynklib.Blynk(BLYNK_AUTH, log=_log.info)

# uncomment line below if simple printing will be used instead of logging
# blynk = blynklib.Blynk(BLYNK_AUTH, log=print)

WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_PIN_EVENT] Pin: V{} Value: '{}'"
TWEET_MSG = "New value='{}' on VPIN({})"


# register handler for virtual pin V7 write event
@blynk.handle_event('write V7')
def write_virtual_pin_handler(pin, value):
    _log.info(WRITE_EVENT_PRINT_MSG.format(pin, value))
    blynk.tweet(TWEET_MSG.format(pin, value))


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
