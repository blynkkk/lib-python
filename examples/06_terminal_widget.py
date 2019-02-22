# todo add caption and finish

import blynklib
import subprocess

BLYNK_AUTH = 'YourAuthToken'
USB_DEV_PATTERN = 'YourPattern ex. Mp3 player'

blynk = blynklib.Blynk(BLYNK_AUTH)


@blynk.handle_event('write V22')
def write_handler(pin, values):
    print(values)
    if values and values[0] == u'lsusb':
        found_usb_dev = subprocess.check_output("lsusb")
        dev_list = found_usb_dev.split('\n')
        target_dev_list = [dev_rec for dev_rec in dev_list if USB_DEV_PATTERN in dev_rec]
        print('{}'.format(target_dev_list))
        blynk.virtual_write(pin, *target_dev_list)
        print('=' * 20)


###########################################################
# infinite loop that waits for event
###########################################################
while True:
    blynk.run()
