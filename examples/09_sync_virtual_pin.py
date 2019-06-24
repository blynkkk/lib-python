"""
[VIRTUAL PIN SYNC EXAMPLE] ==========================================================================================

Environment prepare:
In your Blynk App project:
  - add 3 "Button" widgets,
  - bind then to Virtual Pins V0, V1, v2
  - set mode "SWITCH" for all of them
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example and run it


This started program will restore on connect write_virtual_pin states and colors.
Buttons states and colors can be modified during script run.
If script was interrupted (KeyboardInterrupt) buttons colors will be changed to red.
During next connect event ( script re-run) previous buttons states and colors will be restored.

Schema:
=====================================================================================================================
          +-----------+                        +--------------+                    +--------------+
          |           |                        |              |                    |              |
          | blynk lib |                        | blynk server |                    |  blynk app   |
          |           |                        |  virtual pin |                    |              |
          |           |                        |              |                    |              |
          +-----+-----+                        +------+-------+                    +-------+------+
connect handler |                                     |                                    |
       +--------+                                     |                                    |
       |        +------------------------------------>+                                    |
       |        |  virtual pin sync                   |                                    |
       |        +<------------------------------------+----------------------------------->+
       |        |    virtual pin write stored value   |         send pin value to app      |
       |        +<------------------------------------+----------------------------------->+
       |        | virtual pin apply stored properties |        send pin properties to app  |
       +------->+                                     |                                    |
  write handler |                                     |                                    |
       +--------+                                     +<-----------------------------------+
       |        +<------------------------------------+            write event from button |
       +>------>+            write event form server  |                                    |
                |                                     |                                    |
                |                                     |                                    |
    disconnect  |                                     |                                    |
       handler  |                                     |                                    |
        +-------+                                     |                                    |
        |       +------------------------------------>+                                    |
        +------>+ set new virtual pin property        |                                    |
                |                                     |                                    |
                |                                     |                                    |
                |                                     |                                    |
                +                                     +                                    +

=====================================================================================================================
Additional info about blynk you can find by examining such resources:

    Downloads, docs, tutorials:     https://blynk.io
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================================
"""
import logging
import blynklib

# tune console logging
_log = logging.getLogger('BlynkLog')
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
_log.addHandler(consoleHandler)
_log.setLevel(logging.DEBUG)

colors = {'1': '#FFC300', '0': '#CCCCCC', 'OFFLINE': '#FF0000'}

BLYNK_AUTH = 'YourAuthToken'
blynk = blynklib.Blynk(BLYNK_AUTH, log=_log.info)


@blynk.handle_event("connect")
def connect_handler():
    _log.info('SCRIPT_START')
    for pin in range(3):
        _log.info('Syncing virtual pin {}'.format(pin))
        blynk.virtual_sync(pin)

        # within connect handler after each server send operation forced socket reading is required cause:
        #  - we are not in script listening state yet
        #  - without forced reading some portion of blynk server messages can be not delivered to HW
        blynk.read_response(timeout=0.5)


@blynk.handle_event('write V*')
def write_handler(pin, value):
    button_state = value[0]
    blynk.set_property(pin, 'color', colors[button_state])


@blynk.handle_event("disconnect")
def connect_handler():
    for pin in range(3):
        _log.info("Set 'OFFLINE' color for pin {}".format(pin))
        blynk.set_property(pin, 'color', colors['OFFLINE'])


###########################################################
# infinite loop that waits for event
###########################################################
try:
    while True:
        blynk.run()
except KeyboardInterrupt:
    blynk.disconnect()
    _log.info('SCRIPT WAS INTERRUPTED')
