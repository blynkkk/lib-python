"""
[APP CONNECT DISCONNECT EVENTS EXAMPLE] ============================================================

Environment prepare:
In your Blynk App project:
  - in Project Settings enable flag "Notify devices when APP connected"
  - define your auth token for current example and run it
  - Run the App (green triangle in the upper right corner).

This started program will call handlers and print messages for APP_CONNECT or APP_DISCONNECT events.

Schema:
====================================================================================================
          +-----------+                        +--------------+                    +--------------+
          |           |                        |              |                    |              |
          | blynk lib |                        | blynk server |                    |  blynk app   |
          |           |                        |  virtual pin |                    |              |
          |           |                        |              |                    |              |
          +-----+-----+                        +------+-------+                    +-------+------+
                |                                     |    app connected or disconnected   |
                |                                     |             from server            |
                                                      |                                    |
 event handler  |     app connect/disconnect event    +<-----------------------------------+
(user function) |                                     |                                    |
     +------------<-----------------------------------+                                    |
     |          |                                     |                                    |
     |          |                                     |                                    |
     +--------->+                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                +                                     +                                    +
====================================================================================================
Additional blynk info you can find by examining such resources:

    Downloads, docs, tutorials:     https://blynk.io
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

APP_CONNECT_PRINT_MSG = '[APP_CONNECT_EVENT]'
APP_DISCONNECT_PRINT_MSG = '[APP_DISCONNECT_EVENT]'


@blynk.handle_event('internal_acon')
def app_connect_handler(*args):
    print(APP_CONNECT_PRINT_MSG)


@blynk.handle_event('internal_adis')
def app_disconnect_handler(*args):
    print(APP_DISCONNECT_PRINT_MSG)


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
