# todo add caption and finish

import time
import blynklib
import subprocess

BLYNK_AUTH = 'YourAuthToken'
USB_DEV_PATTERN = 'Linux'

blynk = blynklib.Blynk(BLYNK_AUTH)


@blynk.handle_event("connect")
def connect_handler():
    print('smth')
    blynk.virtual_write(22, 'Command22:')


@blynk.handle_event('write V22')
def write_handler(pin, values):
    if values and values[0] == u'lsusb':
        found_usb_dev = subprocess.check_output("lsusb")
        dev_list = found_usb_dev.split('\n')
        target_dev_list = [dev_rec for dev_rec in dev_list if USB_DEV_PATTERN in dev_rec]
        print('{}'.format(target_dev_list))
        print('=' * 20)
        # todo understand why this is not working always
        blynk.virtual_write(22, 'USB: 123\n')


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
