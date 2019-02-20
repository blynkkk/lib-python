"""
[CONNECT/DISCONNECT EVENTS EXAMPLE] =================================================================

Environment prepare:
    - define your auth token for current example and run it


This started program after successful connect operation will call and execute "connect event handler"
Within handler after short sleep delay blynk disconnect call will be performed that will trigger
"disconnect event handler" execution.

Schema:
=====================================================================================================
              +-----------+                        +--------------+
              |           |                        |              |
              | blynk lib |                        | blynk server |
              |           |                        |  virtual pin |
              |           |                        |              |
              +-----+-----+                        +------+-------+
                    |                                     |
                    |      connect/authenticate request   |
                    +------------------------------------>+
   connect handler  |                                     |
    (user function) |        connected successfully       |
         +-----------<------------------------------------+
         |          |                                     |
         |          |          disconnect request         |
         +--------->------------------------------------->+
                    |                                     |
                    |                                     |
disconnect handler  |                                     |
    (user function) |      disconnected successfully      |
         +-----------<------------------------------------+
         |          |                                     |
         |          |                                     |
         +--------->+                                     |
                    |          reconnect request          |
                    |    performed by lib automatically   |
                    +------------------------------------>+
                    +                                     +


====================================================================================================
Additional info about blynk you can find by examining such resources:

    Downloads, docs, tutorials:     http://www.blynk.cc
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================
"""

import blynklib

try:
    import time
except ImportError:
    # micropython support
    import utime as time

BLYNK_AUTH = 'YourAuthToken'

blynk = blynklib.Blynk(BLYNK_AUTH)

CONNECT_PRINT_MSG = '[CONNECT_EVENT]'
DISCONNECT_PRINT_MSG = '[DISCONNECT_EVENT]'


@blynk.handle_event("connect")
def connect_handler():
    print(CONNECT_PRINT_MSG)
    print('Sleeping 2 sec in connect handler...')
    time.sleep(2)
    blynk.disconnect()


@blynk.handle_event("disconnect")
def connect_handler():
    print(DISCONNECT_PRINT_MSG)
    print('Sleeping 4 sec in disconnect handler...')
    time.sleep(4)


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
