"""
[EMAIL ON CONNECT EXAMPLE] ==========================================================================================

Environment prepare:
In your Blynk App project:
  - add "Email" widget,
  - Run the App (green triangle in the upper right corner).
  - define for current example your target email.
  - define your auth token for current example and run it


This started program will operate with "connect_handler".
Within handler after short sleep delay email send operation will be performed.

Schema:
=====================================================================================================================
           +-----------+                        +--------------+                    +--------------+      +-------+
           |           |                        |              |                    |              |      |       |
           | blynk lib |                        | blynk server |                    |  blynk app   |      | email |
           |           |                        |  virtual pin |                    |              |      |  box  |
           |           |                        |              |                    |              |      |       |
           +-----+-----+                        +------+-------+                    +-------+------+      +---+----
                 |           connect request           |                                    |                 |
                 +------------------------------------>+                                    |                 |
connect handler  |                                     |                                    |                 |
 (user function) |        connected successfully       |                                    |                 |
      +-----------<------------------------------------+                                    |                 |
      |          |                                     |                                    |                 |
      |          |             send email              |        email widget present?       |                 |
      +--------->------------------------------------->+  (is user allowed to send emails)  |                 |
                 |                                     +----------------------------------->+                 |
                 |                                     |                                    |                 |
                 |                                     |      email sending allowed         |                 |
                 |                                     +<-----------------------------------+                 |
                 |                                     |                                    |                 |
                 |                                     |                                    |                 |
                 |                                     |    send email to defined address   |                 |
                 |                                     +----------------------------------------------------->+
                 |                                     |                                    |                 |
                 |                                     |                                    |                 |
                 +                                     +                                    +                 +


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

try:
    import time
except ImportError:
    # micropython support
    import utime as time

BLYNK_AUTH = 'YourAuthToken'
TARGET_EMAIL = 'YourTargetEmail'

blynk = blynklib.Blynk(BLYNK_AUTH)
EMAIL_PRINT_MSG = "[EMAIL WAS SENT to '{}']".format(TARGET_EMAIL)


@blynk.handle_event("connect")
def connect_handler():
    print('Sleeping 2 sec before sending email...')
    time.sleep(2)
    blynk.email(TARGET_EMAIL, 'BLYNK-HW-TEST-EMAIL', 'Connected!')
    print(EMAIL_PRINT_MSG)


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
