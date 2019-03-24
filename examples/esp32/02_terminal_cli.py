"""
[TERMINAL WIDGET ESP32 EXAMPLE] =====================================================================================

Environment prepare:
In your Blynk App project:
  - add "Terminal" widget,
  - bind it to Virtual Pin V2,
  - add input line option in widget settings
  - Run the App (green triangle in the upper right corner).
  - define your auth token for current example
  - define SSID and WiFi password that will be used by ESP32 board
  - run current example


This started program will call and execute event handler "write_virtual_pin_handler" if new
event comes from terminal app widget.
In App Terminal widget you can type commands.
'help' - info about available commnds
'logo' - prints blynk library ascii logo
'version' - prints blynk library version
'sysinfo' - prints board system info
'ls' - list target board dir. Example: 'ls /lib'.
       root dir will be listed if no arguments provided

For any other terminal inputs will be printed error info that provided command is not supported.
=====================================================================================================================
Additional info about blynk you can find by examining such resources:

    Downloads, docs, tutorials:     https://blynk.io
    Sketch generator:               http://examples.blynk.cc
    Blynk community:                http://community.blynk.cc
    Social networks:                http://www.fb.com/blynkapp
                                    http://twitter.com/blynk_app
=====================================================================================================================
"""
import blynklib
import network
import uos
import utime as time

WIFI_SSID = 'YourWifiSSID'
WIFI_PASS = 'YourWifiPassword'
BLYNK_AUTH = 'YourAuthToken'

print("Connecting to WiFi network '{}'".format(WIFI_SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)
while not wifi.isconnected():
    time.sleep(1)
    print('WiFi connect retry ...')
print('WiFi IP:', wifi.ifconfig()[0])

print("Connecting to Blynk server...")
blynk = blynklib.Blynk(BLYNK_AUTH)

CMD_LIST = ['logo', 'version', 'sysinfo', 'ls']


@blynk.handle_event('write V2')
def write_handler(pin, values):
    if values:
        in_args = values[0].split(' ')
        cmd = in_args[0]
        cmd_args = in_args[1:]

        if cmd == 'help':
            output = ' '.join(CMD_LIST)
        elif cmd == CMD_LIST[0]:
            output = blynklib.LOGO
        elif cmd == CMD_LIST[1]:
            output = blynklib.__version__
        elif cmd == CMD_LIST[2]:
            output = uos.uname()
        elif cmd == CMD_LIST[3]:
            arg = cmd_args[0] if cmd_args else ''
            output = uos.listdir(arg)
        else:
            output = "[ERR]: Not supported command '{}'".format(values[0])

        blynk.virtual_write(pin, output)
        blynk.virtual_write(pin, '\n')


while True:
    blynk.run()
