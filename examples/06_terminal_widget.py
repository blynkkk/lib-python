"""
[TERMINAL WIDGET EXAMPLE] ==========================================================================================

Environment prepare:
In your Blynk App project:
  - add "Terminal" widget,
  - bind it to Virtual Pin V6,
  - add input line option in widget settings
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example
  - optionally you can define your own "ALLOWED_COMMANDS_LIST"
  - run current example


This started program will periodically call and execute event handler "write_virtual_pin_handler".
In App Terminal widget you can type commands. If command present in allowed list, script will try
to execute it in current running environment and will send back to terminal execution results.
Additionally can be used 'help' command to get in terminal list of available commands.

Schema:
=====================================================================================================================
+-----+             +-----------+                        +--------------+                    +--------------+
|     |             |           |                        |              |                    |              |
| env |             | blynk lib |                        | blynk server |                    |  blynk app   |
|     |             |           |                        |  virtual pin |                    |              |
|     |             |           |                        |              |                    |              |
+--+--+             +-----+-----+                        +------+-------+                    +-------+------+
   |                      |                                     |                                    |
   |                      |                                     | write command from terminal widget |
   |                      |                                     |                                    |
   |                      |                                     +<-----------------------------------+
   |       event handler  |   write event to hw from server     |                                    |
   |      (user function) |                                     |                                    |
   |  exec     +-----------<------------------------------------+                                    |
   +<----------+          |                                     |                                    |
   |           |          |      write cmd out back to pin      |                                    |
   +---------->+--------->------------------------------------->+                                    |
   |                      |                                     |           was pin updated?         |
   |                      |                                     +<-----------------------------------+
   |                      |                                     |                                    |
   |                      |                                     |                                    |
   |                      |                                     |  take vpin data to widget output   |
   |                      |                                     |                                    |
   |                      |                                     +----------------------------------->+
   |                      |                                     |                                    |
   +                      +                                     +                                    +

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
import subprocess

BLYNK_AUTH = 'YourAuthToken'

# last command in example - just to show error handling
# for certain HW can be added specific commands. 'gpio readall' on PI3b for example
ALLOWED_COMMANDS_LIST = ['ls', 'lsusb', 'ip a', 'ip abc']

blynk = blynklib.Blynk(BLYNK_AUTH)


@blynk.handle_event('write V6')
def write_handler(pin, values):
    header = ''
    result = ''
    delimiter = '{}\n'.format('=' * 30)
    if values and values[0] in ALLOWED_COMMANDS_LIST:
        cmd_params = values[0].split(' ')
        try:
            result = subprocess.check_output(cmd_params).decode('utf-8')
            header = '[output]\n'
        except subprocess.CalledProcessError as exe_err:
            header = '[error]\n'
            result = 'Return Code: {}\n'.format(exe_err.returncode)
        except Exception as g_err:
            print("Command caused '{}'".format(g_err))
    elif values and values[0] == 'help':
        header = '[help -> allowed commands]\n'
        result = '{}\n'.format('\n'.join(ALLOWED_COMMANDS_LIST))

    # communicate with terminal if help or some allowed command
    if result:
        output = '{}{}{}{}'.format(header, delimiter, result, delimiter)
        print(output)
        blynk.virtual_write(pin, output)
        blynk.virtual_write(pin, '\n')


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
