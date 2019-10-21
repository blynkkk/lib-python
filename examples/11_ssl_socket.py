"""
[SSL CONNECT/DISCONNECT EVENTS EXAMPLE] =================================================================
NOTE!
    This example works correctly only fo cPython version of library (blynklib.py)
    For micropython present limitation that keyword arguments of wrap_socket may be not supported by certain ports


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

    Downloads, docs, tutorials:     https://blynk.io
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================
"""

import blynklib
import time
import logging

# tune console logging
_log = logging.getLogger('BlynkLog')
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
_log.addHandler(consoleHandler)
_log.setLevel(logging.DEBUG)

BLYNK_AUTH = 'YourAuthToken'

blynk = blynklib.Blynk(BLYNK_AUTH, port=443, ssl_cert='../certificate/blynk-cloud.com.crt', log=_log.info)

CONNECT_PRINT_MSG = '[CONNECT_EVENT]'
DISCONNECT_PRINT_MSG = '[DISCONNECT_EVENT]'


@blynk.handle_event("connect")
def connect_handler():
    print(CONNECT_PRINT_MSG)
    print('Sleeping 4 sec in SSL connect handler...')
    time.sleep(4)
    blynk.disconnect()


@blynk.handle_event("disconnect")
def disconnect_handler():
    print(DISCONNECT_PRINT_MSG)
    print('Sleeping 3 sec in SSL disconnect handler...')
    time.sleep(5)


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
