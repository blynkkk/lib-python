"""
[RTC EXAMPLE] ========================================================================================================

Environment prepare:
In your Blynk App project:
  - add "RTC" widget,
  - set required TimeZone,
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example and run it


This started program on connect will send rtc_sync call to server.
RTC reply will be captured by "internal_rtc" handler
UTC time with required timezone correction will be printed

Schema:
=====================================================================================================================
           +-----------+                        +--------------+                    +--------------+
           |           |                        |              |                    |              |
           | blynk lib |                        | blynk server |                    |  blynk app   |
           |           |                        |              |                    |              |
           |           |                        |              |                    |              |
           +-----+-----+                        +------+-------+                    +-------+------+
                 |                                     |                                    |
connect handler  |                                     |                                    |
         +-------+                                     |                                    |
         |       |                                     |                                    |
         |       |        rtc sync                     |                                    |
         +------>------------------------------------->+        rtc widget present in app?  |
                 |                                     +----------------------------------->+
                 |                                     |                                    |
                 |                                     |           yes rtc widget found     |
                 |    rtc with timezone correction     +<-----------------------------------+
internal_rtc     |                                     |                                    |
handler  +--------<------------------------------------+                                    |
         |       |                                     |                                    |
         |       |                                     |                                    |
         +------>+                                     |                                    |
                 |                                     |                                    |
                 |                                     |                                    |
                 +                                     +                                    +
=====================================================================================================================
Additional blynk info you can find by examining such resources:

    Downloads, docs, tutorials:     https://blynk.io
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================================
"""

import blynklib
from datetime import datetime

BLYNK_AUTH = 'YourAuthToken'
blynk = blynklib.Blynk(BLYNK_AUTH)


@blynk.handle_event("connect")
def connect_handler():
    blynk.internal("rtc", "sync")
    print("RTC sync request was sent")


@blynk.handle_event('internal_rtc')
def rtc_handler(rtc_data_list):
    hr_rtc_value = datetime.utcfromtimestamp(int(rtc_data_list[0])).strftime('%Y-%m-%d %H:%M:%S')
    print('Raw RTC value from server: {}'.format(rtc_data_list[0]))
    print('Human readable RTC value: {}'.format(hr_rtc_value))


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
